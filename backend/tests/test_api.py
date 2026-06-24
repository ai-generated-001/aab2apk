import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.converter import task_manager

client = TestClient(app)

def test_root_endpoint():
    """Verify that root endpoint is online and returns expected metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "AAB to APK Converter" in data["service"]

def test_upload_invalid_file_extension():
    """Verify that uploading files without .aab extension fails with a 400 Bad Request."""
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Only .aab files are allowed" in response.json()["detail"]

def test_get_nonexistent_task():
    """Verify that querying a nonexistent task returns a 404 Not Found."""
    response = client.get("/api/tasks/invalid_task_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."

def test_download_nonexistent_task():
    """Verify that downloading from a nonexistent task returns a 404 Not Found."""
    response = client.get("/api/tasks/invalid_task_id/download")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."

@pytest.mark.asyncio
async def test_task_creation_and_retrieval(tmp_path):
    """Verify that task creation saves state and allows retrieval via GET."""
    task_id = "test_task_123"
    temp_dir = tmp_path
    aab_path = tmp_path / "app.aab"
    
    # Pre-populate TaskManager
    await task_manager.create_task(task_id, temp_dir, aab_path)
    
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "PENDING"
    assert data["progress"] == 0
    assert len(data["logs"]) > 0
    
    # Cleanup task manager
    if task_id in task_manager.tasks:
        del task_manager.tasks[task_id]
