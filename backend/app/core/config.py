import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Polyglot Media Analyzer"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered multilingual media analysis platform"
    
    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/polyglot_media"
    
    # ElasticSearch Settings
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "media_content"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS: list = [".mp4", ".avi", ".mov", ".mp3", ".wav", ".m4a"]
    
    # Hugging Face Settings
    HF_TOKEN: Optional[str] = None
    
    # AI Model Settings
    ASR_MODEL: str = "openai/whisper-base"
    TRANSLATION_MODEL: str = "Helsinki-NLP/opus-mt-en-mul"
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    OBJECT_DETECTION_MODEL: str = "facebook/detr-resnet-50"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)