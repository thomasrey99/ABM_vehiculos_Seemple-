from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.services.storage.models.uploaded_file_info import UploadedFileInfo


class StorageService(ABC):

    @abstractmethod
    async def upload_file(
        self,
        file: UploadFile,
        destination: str,
    ) -> UploadedFileInfo:
        ...

    @abstractmethod
    async def delete_file(
        self,
        file_url: str,
    ) -> None:
        ...