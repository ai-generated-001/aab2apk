import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "AAB to APK Converter"
    
    # Bundletool Settings
    BUNDLETOOL_VERSION: str = "1.18.3"
    BUNDLETOOL_DIR: Path = Path("/app/bin")
    
    @property
    def BUNDLETOOL_PATH(self) -> Path:
        return self.BUNDLETOOL_DIR / "bundletool.jar"
    
    @property
    def BUNDLETOOL_URL(self) -> str:
        return f"https://github.com/google/bundletool/releases/download/{self.BUNDLETOOL_VERSION}/bundletool-all-{self.BUNDLETOOL_VERSION}.jar"
        
    # Directories for processing
    UPLOAD_DIR: Path = Path("/tmp/aab2apk/uploads")
    OUTPUT_DIR: Path = Path("/tmp/aab2apk/outputs")
    
    # Retention period for completed or failed task folders (in seconds)
    TASK_RETENTION_SECONDS: int = 1800  # 30 minutes
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
