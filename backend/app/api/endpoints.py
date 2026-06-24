import asyncio
import os
import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.utils.file_helper import generate_task_id, sanitize_filename, ensure_directory
from app.services.converter import task_manager, run_conversion_task

router = APIRouter(prefix="/api")

@router.post("/upload")
async def upload_aab(file: UploadFile = File(...)):
    """
    Accepts an AAB file, generates a unique task ID, saves the file chunk-by-chunk 
    to a secure temp folder, and schedules the conversion background task.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".aab"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only .aab files are allowed."
        )
    
    # 1. Initialize Task ID and Secure Directories
    task_id = generate_task_id()
    temp_dir = settings.UPLOAD_DIR / task_id
    ensure_directory(temp_dir)
    
    sanitized_name = sanitize_filename(filename)
    aab_path = temp_dir / sanitized_name
    
    # 2. Write file asynchronously in chunks
    try:
        async with aiofiles.open(aab_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # 1MB chunk size
                await out_file.write(chunk)
    except Exception as e:
        # Clean up temp directory on failure
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save uploaded file: {str(e)}"
        )
    finally:
        await file.close()

    # 3. Create the task state in task manager
    await task_manager.create_task(task_id, temp_dir, aab_path)
    
    # 4. Fire-and-forget the background converter task
    asyncio.create_task(run_conversion_task(task_id))
    
    return {"task_id": task_id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Returns the current status, logs, and progress percentage for the given task.
    """
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
        
    return {
        "task_id": task["id"],
        "status": task["status"],
        "progress": task["progress"],
        "logs": task["logs"],
        "error": task["error"],
        "created_at": task["created_at"].isoformat()
    }


@router.get("/tasks/{task_id}/download")
async def download_apk(task_id: str):
    """
    Downloads the final universal APK.
    """
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
        
    if task["status"] != "SUCCESS":
        raise HTTPException(
            status_code=400, 
            detail=f"Task is in state '{task['status']}' and not ready for download."
        )
        
    apk_path = task["apk_path"]
    if not apk_path or not apk_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Compiled APK file was not found on disk."
        )
        
    # Generate clean name for download download
    aab_filename = task["aab_path"].stem
    download_name = f"{aab_filename}-universal.apk"
    
    return FileResponse(
        path=apk_path,
        media_type="application/vnd.android.package-archive",
        filename=download_name
    )
