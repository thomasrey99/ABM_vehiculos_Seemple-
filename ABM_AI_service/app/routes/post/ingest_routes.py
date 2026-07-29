from typing import List, Annotated
from app.routes.router import appRouter
from fastapi import File, UploadFile, Form
from app.controllers.post.ingest_controller import ingest_controller
from app.schemas.response import APIResponse, IndexedImageResponse


@appRouter.post("/ingest", response_model=APIResponse[List[IndexedImageResponse]])
async def ingest_endpoint(
    vehicle_id: Annotated[str, Form(description="UUID del vehiculo")],
    license_plate: Annotated[str, Form(description="Patente del vehiculo (provista por el backend)")],
    brand: Annotated[str, Form(description="Marca del vehiculo (ej: Toyota)")],
    model: Annotated[str, Form(description="Modelo del vehiculo (ej: Corolla)")],
    color: Annotated[str, Form(description="Color del vehiculo (ej: blanco)")],
    labels: Annotated[
        List[str], Form(description="Etiquetas descriptivas para cada imagen")
    ],
    files: Annotated[List[UploadFile], File(description="Archivos de imagen")],
    details: Annotated[
        List[str],
        Form(description="Detalles adicionales del vehiculo (ej: rayón en puerta izquierda)")
    ] = [],
):
    """
    Endpoint para subir e indexar un lote de imágenes asociadas a un vehiculo
    mediante su ID, junto con sus metadatos (patente, marca, modelo, color,
    detalles). La patente ya no se detecta por ANPR en este endpoint: la
    provee directamente el backend, que ya la tiene validada como dato del
    vehículo. El ANPR se usa únicamente en /search/image.
    """
    
    return await ingest_controller(vehicle_id, files, labels, license_plate, brand, model, color, details)