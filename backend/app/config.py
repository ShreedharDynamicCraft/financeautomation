import os
import logging
import json
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # App settings
    app_name: str = "PDF Data Extractor"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS settings - Allow all origins by default, can be customized via env
    cors_origins: List[str] = ["*"]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma
                return [origin.strip() for origin in v.split(',')]
        return v
    
    # Google Gemini API
    google_api_key: str = ""  # Set this in .env file
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # File upload settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "uploads"
    output_dir: str = "outputs"
    allowed_extensions: list[str] = [".pdf"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Task settings
    task_timeout: int = 300  # 5 minutes
    max_retries: int = 3
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Create directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ]
)

logger = logging.getLogger(__name__)