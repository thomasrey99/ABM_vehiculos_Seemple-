from typing import List, Annotated
from app.routes.router import appRouter
from fastapi import File, UploadFile, Form
from app.controllers.post.ingest_controller import ingest_controller
from app.schemas.response import APIResponse, IndexedImageResponse


@appRouter.post("/ingest", response_model=APIResponse[List[IndexedImageResponse]])
async def ingest_endpoint(
    vehicle_id: Annotated[str, Form(description="UUID del vehiculo")],
    brand: Annotated[str, Form(description="Marca del vehiculo (ej: Toyota)")],
    model: Annotated[str, Form(description="Modelo del vehiculo (ej: Corolla)")],
    color: Annotated[str, Form(description="Color del vehiculo (ej: blanco)")],
    labels: Annotated[
        List[str], Form(description="Etiquetas descriptivas para cada imagen")
    ],
    files: Annotated[List[UploadFile], File(description="Archivos de imagen")],
    details: Annotated[
        List[str],
        Form(
            description=(
                "Detalle específico de CADA imagen, en el mismo orden y "
                "cantidad que labels/files (ej: '' para la de frente, "
                "'rayón puerta izquierda' para la de esa imagen puntual). "
                "Enviar cadena vacía para las imágenes sin detalle."
            )
        )
    ] = [],
):
    """
    Endpoint para subir e indexar un lote de imágenes asociadas a un vehiculo
    mediante su ID. `brand`/`model`/`color` son atributos del vehículo
    completo. `details` es un atributo POR IMAGEN (un detalle está asociado
    al sector fotografiado, ej. "rayón" va con la foto que muestra ese
    sector, no con todas). La patente (license_plate) se detecta
    automáticamente de las imágenes mediante ANPR, no se recibe como
    parámetro.
    """
    return await ingest_controller(vehicle_id, files, labels, brand, model, color, details)