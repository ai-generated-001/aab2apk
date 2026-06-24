import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import router as api_router
from app.services.converter import ensure_bundletool_exists, task_cleanup_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    # 1. Ensure working and temporary directories exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Trigger asynchronous bundletool verification & fetch if needed
    asyncio.create_task(ensure_bundletool_exists())
    
    # 3. Start the background cleanup worker
    cleanup_task = asyncio.create_task(task_cleanup_loop())
    
    yield
    
    # Shutdown actions
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous Android App Bundle (.aab) to APK (.apk) conversion API.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }
