from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fortress AI"
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Fireworks AI ──────────────────────────────────────────
    FIREWORKS_URL: str = "https://api.fireworks.ai/inference/v1"
    FIREWORKS_API_KEY: str = ""

    QWEN_MODEL: str = "accounts/fireworks/models/qwen3p6-plus"
    KIMI_MODEL: str = "accounts/fireworks/models/kimi-k2p5"

    # ── Qdrant (future RAG) ──────────────────────────────────
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "legal_documents"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

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
