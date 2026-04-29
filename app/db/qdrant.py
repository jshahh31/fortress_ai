from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

# Global async client
client = AsyncQdrantClient(url=settings.QDRANT_URL)

async def init_qdrant():
    """Initialize the Qdrant collection if it doesn't exist."""
    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]
    
    if settings.QDRANT_COLLECTION not in collection_names:
        # BAAI/bge-m3 has a dimension of 1024
        await client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

async def get_qdrant_client() -> AsyncQdrantClient:
    return client
