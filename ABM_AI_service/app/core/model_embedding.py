from sentence_transformers import SentenceTransformer
from app.config.settings import settings

model=SentenceTransformer(settings.MODEL)