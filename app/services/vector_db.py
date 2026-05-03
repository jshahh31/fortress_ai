"""
Vector Database Service — Qdrant integration.

Handles:
- Collection initialization
- Document chunking and embedding (via fastembed)
- Vector search (RAG)
"""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QRANT_URL if hasattr(settings, 'QRANT_URL') else settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION
        self._model: Optional[TextEmbedding] = None

    @property
    def model(self) -> TextEmbedding:
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        return self._model

    async def init_collection(self):
        """Initialize the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.info(f"Creating collection: {self.collection_name}")
                # BGE-M3 usually has 1024 dimensions
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1024, 
                        distance=models.Distance.COSINE
                    ),
                )
            else:
                logger.info(f"Collection {self.collection_name} already exists.")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")

    async def add_documents(self, text: str, metadata: Dict[str, Any]):
        """Chunk, embed, and add a document to the vector store."""
        # Simple chunking for now (can be improved)
        chunks = self._chunk_text(text)
        
        # Embed chunks
        logger.info(f"Embedding {len(chunks)} chunks for {metadata.get('filename', 'unknown')}")
        embeddings = list(self.model.embed(chunks))
        
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append(models.PointStruct(
                id=f"{metadata.get('file_id', 'doc')}_{i}",
                vector=vector.tolist(),
                payload={
                    **metadata,
                    "content": chunk,
                    "chunk_index": i
                }
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Successfully indexed {len(points)} points.")

    async def search(self, query: str, limit: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Search for relevant document chunks."""
        query_vector = list(self.model.embed([query]))[0]
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            query_filter=models.Filter(**filter_dict) if filter_dict else None,
            limit=limit
        )
        
        return [hit.payload for hit in search_result]

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

# Singleton instance
vector_db = VectorDBService()
