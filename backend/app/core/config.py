from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Autonomous Legal Reasoning Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database (SQLite — no setup needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/legal_reasoning.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Groq — PRIMARY LLM (free at console.groq.com)
    GROQ_API_KEY: str
    GROQ_DEBATE_ROUNDS: int = 3
    GROQ_MODELS: str = "llama-3.3-70b-versatile,llama-3.1-8b-instant"

    # Google Gemini (optional — fallback/alternative)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 4000

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "legal_documents"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./data/uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
