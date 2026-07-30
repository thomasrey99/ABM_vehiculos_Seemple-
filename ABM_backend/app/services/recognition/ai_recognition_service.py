import asyncio
import json
from uuid import UUID

import httpx
import requests
from fastapi import UploadFile

from app.core.logging import logger
from app.core.settings import settings
from app.services.recognition.models.image_search_result import (
    ImageMatchDetail,
    ImageSearchResult,
    VehicleImageMatch,
)
from app.services.recognition.recognition_service import RecognitionService


class AIRecognitionService(RecognitionService):

    async def index_images(
        self,
        vehicle_id: UUID,
        license_plate: str,
        brand: str,
        model: str,
        color: str,
        images: list[tuple[UploadFile, str, list[str]]],
    ) -> list[str | None]:

        metadata = {
            "vehicle_id": str(vehicle_id),
            "brand": brand,
            "model": model,
            "color": color,
            "license_plate": license_plate,
            "images": [
                {"label": label, "details": details}
                for _, label, details in images
            ],
        }

        data = {"metadata": json.dumps(metadata)}

        files_payload = []

        for upload_file, _, _ in images:
            await upload_file.seek(0)
            content = await upload_file.read()

            files_payload.append(
                (
                    "files",
                    (upload_file.filename, content, upload_file.content_type),
                )
            )

        headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}

        # Se usa `requests` (en un thread aparte) en lugar de
        # httpx.AsyncClient: esta combinación de versiones de
        # httpx/httpcore/h11 tiene un bug real en la codificación
        # multipart en Python 3.14 (TypeError dentro de h11._connection.send
        # / RuntimeError "Attempted to send an sync request...").
        response = await asyncio.to_thread(
            requests.post,
            f"{settings.AI_SERVICE_URL}/ingest",
            headers=headers,
            data=data,
            files=files_payload,
            timeout=settings.AI_SERVICE_TIMEOUT,
        )

        response.raise_for_status()

        body = response.json()

        if not body.get("success"):
            raise RuntimeError(
                body.get(
                    "message",
                    "El servicio de reconocimiento devolvió un error.",
                )
            )

        results = body.get("data") or []

        if len(results) != len(images):
            logger.warning(
                "El servicio de reconocimiento devolvió %s resultados "
                "para %s imágenes enviadas (vehicle_id=%s). Se descarta "
                "el resultado por no poder garantizar la correspondencia.",
                len(results),
                len(images),
                vehicle_id,
            )
            return [None] * len(images)

        return [result.get("embedding_id") for result in results]
    
    async def search_by_image(
        self,
        file: UploadFile,
    ) -> ImageSearchResult:

        await file.seek(0)
        content = await file.read()

        files_payload = [
            ("file", (file.filename, content, file.content_type)),
        ]

        headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}

        response = await asyncio.to_thread(
            requests.post,
            f"{settings.AI_SERVICE_URL}/search/image",
            headers=headers,
            files=files_payload,
            timeout=settings.AI_SERVICE_TIMEOUT,
        )

        response.raise_for_status()

        body = response.json()

        if not body.get("success"):
            raise RuntimeError(
                body.get(
                    "message",
                    "El servicio de reconocimiento devolvió un error.",
                )
            )

        data = body.get("data") or {}

        matches = [
            VehicleImageMatch(
                vehicle_id=match.get("vehicle_id"),
                images=[
                    ImageMatchDetail(
                        score=image.get("score"),
                        label=image.get("label"),
                    )
                    for image in match.get("images", [])
                ],
            )
            for match in data.get("matches", [])
        ]

        return ImageSearchResult(
            matches=matches,
            threshold=data.get("threshold"),
        )

    async def delete_by_id(
        self,
        vehicle_id: UUID,
    ) -> None:

        headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}

        # Acá sí se puede usar httpx.AsyncClient sin problemas: es un DELETE
        # simple sin multipart, y ya confirmamos que ese caso funciona bien
        # en este entorno (el bug reproducido era específico de multipart).
        async with httpx.AsyncClient(
            timeout=settings.AI_SERVICE_TIMEOUT,
            trust_env=False,
        ) as client:
            response = await client.delete(
                f"{settings.AI_SERVICE_URL}/delete/{vehicle_id}",
                headers=headers,
            )

        response.raise_for_status()

        body = response.json()

        if not body.get("success"):
            raise RuntimeError(
                body.get(
                    "message",
                    "El servicio de reconocimiento devolvió un error "
                    "al eliminar.",
                )
            )
            
    async def update_vehicle_metadata(
        self,
        vehicle_id: UUID,
        fields: dict[str, str],
    ) -> int:

        headers = {"X-API-Key": settings.AI_SERVICE_API_KEY}

        async with httpx.AsyncClient(
            timeout=settings.AI_SERVICE_TIMEOUT,
            trust_env=False,
        ) as client:
            response = await client.patch(
                f"{settings.AI_SERVICE_URL}/vehicles/{vehicle_id}",
                headers=headers,
                json=fields,
            )

        response.raise_for_status()

        body = response.json()

        if not body.get("success"):
            raise RuntimeError(
                body.get(
                    "message",
                    "El servicio de reconocimiento devolvió un error "
                    "al actualizar metadatos.",
                )
            )

        data = body.get("data") or {}

        return data.get("updated_images", 0)