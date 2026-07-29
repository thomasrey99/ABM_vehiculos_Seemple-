from qdrant_client import QdrantClient, AsyncQdrantClient
from app.config.settings import settings

async_client = AsyncQdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=30.0
)

sync_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=30.0
)