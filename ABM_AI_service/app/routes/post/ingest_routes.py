from typing import List, Annotated
from fastapi import File, UploadFile, Form
from app.routes.router import appRouter
from app.controllers.post.ingest_controller import ingest_controller
from app.schemas.response import APIResponse, IndexedImageResponse


@appRouter.post("/ingest", response_model=APIResponse[List[IndexedImageResponse]])
async def ingest_endpoint(
    metadata: Annotated[
        str,
        Form(
            description=(
                "JSON con los datos del vehículo y la lista de imágenes. "
                "Formato: {\"vehicle_id\": \"...\", \"brand\": \"...\", "
                "\"model\": \"...\", \"color\": \"...\", \"license_plate\": \"...\", "
                "\"images\": [{\"label\": \"frente\", \"details\": []}, "
                "{\"label\": \"atras\", \"details\": [\"abolladura\", \"vidrio roto\"]}]}"
            )
        ),
    ],
    files: Annotated[
        List[UploadFile],
        File(description="Archivos de imagen, en el MISMO ORDEN que 'images' dentro de metadata"),
    ],
):
    """
    Endpoint de ingesta simplificado: un único campo `metadata` (JSON) con
    los datos del vehículo (compartidos) + la lista de imágenes, cada una
    con su `label` (UN sector) y `details` (CERO o más). `files` va en el
    mismo orden posicional que `metadata.images`. La patente se recibe
    manualmente dentro de `metadata` — el ANPR es exclusivo de
    `/search/image`, no se usa en la ingesta.
    """
    return await ingest_controller(metadata, files)