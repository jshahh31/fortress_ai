from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    
    # Qdrant Settings
    QDRANT_URL: str
    QDRANT_COLLECTION: str
    EMBEDDING_MODEL: str
    
    # vLLM Endpoints
    VLLM_QWEN_URL: str
    VLLM_GEMMA_URL: str
    
    # Optional API Keys if vLLM requires them
    VLLM_API_KEY: str
    
    # Model Names configured in vLLM
    QWEN_MODEL_NAME: str
    GEMMA_MODEL_NAME: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
