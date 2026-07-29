from fastapi import UploadFile, File, Path
from app.routes.router import appRouter
from app.controllers.patch.replace_image_controller import replace_image_controller
from app.schemas.response import APIResponse, IndexedImageResponse


@appRouter.patch("/images/{embedding_id}", response_model=APIResponse[IndexedImageResponse])
async def replace_image_endpoint(
    embedding_id: str = Path(..., description="El ID del embedding/imagen a reemplazar"),
    file: UploadFile = File(..., description="Nueva imagen para regenerar el embedding"),
):
    """
    Reemplaza la imagen (embedding) de un punto ya indexado, conservando el
    resto de sus metadatos (vehicle_id, label, brand, model, color,
    license_plate, details).
    """
    return await replace_image_controller(embedding_id, file)