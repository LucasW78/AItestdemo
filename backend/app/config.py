"""
Configuration management for AItestdemo application.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "AItestdemo API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str

    # ChromaDB
    chroma_db_path: str = "/opt/AItestdemo/data/chroma_db"
    chroma_collection_name: str = "documents"

    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"

    # File storage
    upload_dir: str = "/opt/AItestdemo/data/documents"
    max_file_size: int = 52428800  # 50MB
    allowed_extensions: str = "txt,pdf,xls,xlsx,jpg,jpeg,png"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # OCR
    tesseract_cmd: Optional[str] = None

    # Logging
    log_level: str = "INFO"

    @validator("allowed_extensions", pre=True)
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("upload_dir", pre=True)
    def create_upload_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

    @validator("chroma_db_path", pre=True)
    def create_chroma_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()