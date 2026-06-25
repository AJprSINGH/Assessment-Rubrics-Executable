"""
Application Settings
Environment-based configuration for Assessment Rubric Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Application
    APP_NAME: str = "Assessment Rubric Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Intelligence Data
    INTELLIGENCE_CSV_PATH: str = "/workspace/semantic_intelligence.csv"
    
    # Output Directories
    OUTPUT_DIR: str = "outputs"
    PDF_OUTPUT_DIR: str = "outputs/pdfs"
    JSON_OUTPUT_DIR: str = "outputs/jsons"
    LOG_DIR: str = "logs"
    
    # Optional Services
    REDIS_URL: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # LLM Settings (optional)
    LLM_PROVIDER: str = "openai"  # openai, anthropic, deepseek
    LLM_MODEL: str = "gpt-4"
    LLM_API_KEY: Optional[str] = None
    
    # Embeddings (optional)
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
