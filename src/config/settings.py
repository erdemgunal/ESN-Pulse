import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = Field(default="ESN PULSE", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/esn_pulse",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis/Celery
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )
    
    # Scraping Settings
    SCRAPING_DELAY: float = Field(default=0.5, env="SCRAPING_DELAY")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    
    # User Agents for rotation
    USER_AGENTS: List[str] = Field(default=[
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ])
    
    # ESN Platform URLs
    ACCOUNTS_BASE_URL: str = Field(
        default="https://accounts.esn.org",
        env="ACCOUNTS_BASE_URL"
    )
    ACTIVITIES_BASE_URL: str = Field(
        default="https://activities.esn.org",
        env="ACTIVITIES_BASE_URL"
    )
    
    # Logging
    LOG_DIR: str = Field(default="logs", env="LOG_DIR")
    LOG_FILE_FORMAT: str = Field(
        default="esn_pulse_{date}.log",
        env="LOG_FILE_FORMAT"
    )
    
    # Backup Settings
    BACKUP_DIR: str = Field(default="backups", env="BACKUP_DIR")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    # Performance Settings
    PAGINATION_CHUNK_SIZE: int = Field(default=5, env="PAGINATION_CHUNK_SIZE")
    BULK_INSERT_BATCH_SIZE: int = Field(default=100, env="BULK_INSERT_BATCH_SIZE")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8000, env="METRICS_PORT")
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("SCRAPING_DELAY")
    def validate_scraping_delay(cls, v):
        if v < 0.1:
            raise ValueError("SCRAPING_DELAY must be at least 0.1 seconds")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

# Global settings instance
settings = Settings() 