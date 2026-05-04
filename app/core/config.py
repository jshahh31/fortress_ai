from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fortress AI"
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Local AI Models (SSH Tunnel) ──────────────────────────
    QWEN_API_BASE: str = "http://localhost:8001/v1"
    QWEN_MODEL: str = "Qwen/Qwen3.6-27B" 

    GEMMA_API_BASE: str = "http://localhost:8002/v1"
    GEMMA_MODEL: str = "google/gemma-4-E4B"

    LOCAL_API_KEY: str = "dummy-key"

    # ── Qdrant (future RAG) ──────────────────────────────────
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "legal_documents"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    # ── Redis & Celery ────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── File uploads ──────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
