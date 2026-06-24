import os
import shutil
import uuid
import re
from pathlib import Path
from typing import Union

def generate_task_id() -> str:
    """Generate a unique task identifier."""
    return uuid.uuid4().hex

def sanitize_filename(filename: str) -> str:
    """
    Sanitize the file name to prevent directory traversal attacks and other issues.
    Replaces non-alphanumeric (except dot, dash, underscore) characters.
    """
    filename = os.path.basename(filename)
    # Allow alphanumeric, dots, underscores, dashes
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Prevent traversal or empty strings
    if not filename or filename in ('.', '..'):
        filename = f"source_{uuid.uuid4().hex[:8]}.aab"
    return filename

def ensure_directory(path: Union[str, Path]) -> Path:
    """Create directory if it doesn't exist."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def safe_remove_dir(path: Union[str, Path]) -> None:
    """Safely remove a directory and all of its contents."""
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_dir():
        try:
            shutil.rmtree(path_obj)
        except Exception:
            # Silently ignore deletion errors during background cleanups
            pass

def safe_remove_file(path: Union[str, Path]) -> None:
    """Safely remove a file."""
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_file():
        try:
            path_obj.unlink()
        except Exception:
            # Silently ignore deletion errors
            pass
