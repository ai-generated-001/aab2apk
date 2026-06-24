import asyncio
import os
import shutil
import zipfile
import logging
import httpx
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, TypedDict
from app.core.config import settings
from app.utils.file_helper import safe_remove_dir

logger = logging.getLogger("converter")
logging.basicConfig(level=logging.INFO)

class TaskState(TypedDict):
    id: str
    status: str  # PENDING, PROCESSING, SUCCESS, FAILED
    progress: int  # 0 to 100
    logs: List[str]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
    temp_dir: Path
    aab_path: Path
    apks_path: Path
    apk_path: Optional[Path]


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, TaskState] = {}
        self._lock = asyncio.Lock()

    async def create_task(self, task_id: str, temp_dir: Path, aab_path: Path) -> TaskState:
        async with self._lock:
            now = datetime.now(timezone.utc)
            task: TaskState = {
                "id": task_id,
                "status": "PENDING",
                "progress": 0,
                "logs": ["Task created, queued for processing."],
                "error": None,
                "created_at": now,
                "updated_at": now,
                "temp_dir": temp_dir,
                "aab_path": aab_path,
                "apks_path": temp_dir / "output.apks",
                "apk_path": None
            }
            self.tasks[task_id] = task
            return task

    async def get_task(self, task_id: str) -> Optional[TaskState]:
        async with self._lock:
            return self.tasks.get(task_id)

    async def update_task(self, task_id: str, **kwargs) -> Optional[TaskState]:
        async with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                for key, val in kwargs.items():
                    if key in task:
                        task[key] = val  # type: ignore
                task["updated_at"] = datetime.now(timezone.utc)
                return task
            return None

    async def add_log(self, task_id: str, log_line: str) -> None:
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["logs"].append(log_line)
                self.tasks[task_id]["updated_at"] = datetime.now(timezone.utc)

    async def clean_expired_tasks(self) -> None:
        async with self._lock:
            now = datetime.now(timezone.utc)
            expired_ids = []
            for task_id, task in self.tasks.items():
                elapsed = (now - task["created_at"]).total_seconds()
                if elapsed > settings.TASK_RETENTION_SECONDS:
                    expired_ids.append(task_id)
            
            for task_id in expired_ids:
                task = self.tasks[task_id]
                logger.info(f"Cleaning up expired task: {task_id}")
                # Remove temporary files
                safe_remove_dir(task["temp_dir"])
                # Remove from dict
                del self.tasks[task_id]


# Global Task Manager instance
task_manager = TaskManager()


async def ensure_bundletool_exists():
    """Download bundletool.jar if it is not present in bin directory."""
    settings.BUNDLETOOL_DIR.mkdir(parents=True, exist_ok=True)
    jar_path = settings.BUNDLETOOL_PATH
    
    if jar_path.exists():
        logger.info(f"Bundletool already exists at {jar_path}")
        return
        
    url = settings.BUNDLETOOL_URL
    logger.info(f"Downloading bundletool from {url}...")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(jar_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        logger.info(f"Bundletool downloaded successfully to {jar_path}")
    except Exception as e:
        logger.error(f"Error downloading bundletool: {e}")
        # Clean up partial download if any
        if jar_path.exists():
            try:
                jar_path.unlink()
            except Exception:
                pass
        raise e


async def run_conversion_task(task_id: str):
    """
    Background worker that runs the bundletool subprocess, captures logs, 
    and extracts the universal APK.
    """
    task = await task_manager.get_task(task_id)
    if not task:
        logger.error(f"Task {task_id} not found in Manager.")
        return

    try:
        await task_manager.update_task(task_id, status="PROCESSING", progress=10)
        await task_manager.add_log(task_id, "Checking bundletool environment...")
        
        # Check bundletool file
        if not settings.BUNDLETOOL_PATH.exists():
            await task_manager.add_log(task_id, "Downloading bundletool.jar...")
            await ensure_bundletool_exists()
            
        await task_manager.update_task(task_id, progress=20)
        await task_manager.add_log(task_id, "Running bundletool compilation command...")
        
        # Construct the command
        # java -jar bundletool.jar build-apks --bundle=<aab> --output=<apks> --mode=universal
        cmd = [
            "java",
            "-jar",
            str(settings.BUNDLETOOL_PATH),
            "build-apks",
            f"--bundle={task['aab_path']}",
            f"--output={task['apks_path']}",
            "--mode=universal"
        ]
        
        await task_manager.add_log(task_id, f"Executing: {' '.join(cmd)}")
        
        # Start subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Helper to read output streams in real-time
        async def read_stream(stream, is_stderr: bool):
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode('utf-8', errors='replace').strip()
                if line:
                    prefix = "[stderr]" if is_stderr else "[stdout]"
                    await task_manager.add_log(task_id, f"{prefix} {line}")

        # Gather stdout and stderr reading
        await asyncio.gather(
            read_stream(process.stdout, is_stderr=False),
            read_stream(process.stderr, is_stderr=True)
        )
        
        # Wait for the subprocess to terminate
        return_code = await process.wait()
        
        if return_code != 0:
            raise Exception(f"Bundletool process exited with code {return_code}")
            
        await task_manager.update_task(task_id, progress=60)
        await task_manager.add_log(task_id, "Bundletool execution succeeded. Extracting APK set...")
        
        # Verify the generated .apks zip file
        apks_path = task["apks_path"]
        if not apks_path.exists():
            raise Exception("Generated APKS file was not found.")
            
        await task_manager.update_task(task_id, progress=75)
        await task_manager.add_log(task_id, "Locating universal.apk inside the APKS archive...")
        
        # Unzip the universal APK from output.apks
        apk_path = task["temp_dir"] / "app-universal.apk"
        
        with zipfile.ZipFile(apks_path, 'r') as zip_ref:
            apk_names = [name for name in zip_ref.namelist() if name.endswith('.apk')]
            if not apk_names:
                raise Exception("No .apk files found inside the generated APKS zip.")
            
            # Extract first match (typically universal.apk)
            target_apk = apk_names[0]
            await task_manager.add_log(task_id, f"Extracting {target_apk} to final destination...")
            
            with zip_ref.open(target_apk) as z_in, open(apk_path, "wb") as f_out:
                # Copy chunks in a non-blocking thread pool or standard stream copy
                await asyncio.to_thread(shutil.copyfileobj, z_in, f_out)
                
        await task_manager.update_task(
            task_id, 
            status="SUCCESS", 
            progress=100, 
            apk_path=apk_path
        )
        await task_manager.add_log(task_id, "Conversion complete! APK is ready for download.")
        
    except Exception as e:
        logger.exception(f"Error executing task {task_id}")
        await task_manager.update_task(
            task_id, 
            status="FAILED", 
            progress=100, 
            error=str(e)
        )
        await task_manager.add_log(task_id, f"[ERROR] Conversion failed: {str(e)}")


async def task_cleanup_loop():
    """Background task running continuously to clean up expired tasks."""
    while True:
        try:
            await task_manager.clean_expired_tasks()
        except Exception as e:
            logger.error(f"Error in task cleanup loop: {e}")
        await asyncio.sleep(60) # Run cleanup once every minute
