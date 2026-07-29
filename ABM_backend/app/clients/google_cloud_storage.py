import os
from pathlib import Path

from google.cloud import storage

from app.core.settings import settings

BASE_DIR = Path(__file__).resolve().parents[2]
credentials_path = BASE_DIR / settings.GOOGLE_APPLICATION_CREDENTIALS

print("BASE_DIR:", BASE_DIR)
print("Credenciales:", credentials_path)
print("Existe:", credentials_path.exists())

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

storage_client = storage.Client(
    project=settings.GOOGLE_CLOUD_PROJECT_ID
)

bucket = storage_client.bucket(
    settings.GOOGLE_CLOUD_BUCKET
)