import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.clients.google_cloud_storage import bucket
from app.services.storage.models.uploaded_file_info import (
    UploadedFileInfo,
)
from app.services.storage.storage_service import StorageService


class GoogleCloudStorageService(StorageService):

    async def upload_file(
        self,
        file: UploadFile,
        destination: str,
    ) -> UploadedFileInfo:

        extension = Path(file.filename).suffix

        filename = f"{uuid4()}{extension}"

        object_name = (
            f"{destination}/{filename}"
        )

        blob = bucket.blob(object_name)

        await asyncio.to_thread(
            blob.upload_from_file,
            file.file,
            content_type=file.content_type,
        )

        return UploadedFileInfo(
            filename=filename,
            url=(
                f"https://storage.googleapis.com/"
                f"{bucket.name}/{object_name}"
            ),
        )

    async def delete_file(
        self,
        file_url: str,
    ) -> None:

        prefix = (
            f"https://storage.googleapis.com/"
            f"{bucket.name}/"
        )

        object_name = file_url.replace(
            prefix,
            ""
        )

        blob = bucket.blob(object_name)

        await asyncio.to_thread(blob.delete)