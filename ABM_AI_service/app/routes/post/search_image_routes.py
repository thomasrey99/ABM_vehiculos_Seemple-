from fastapi import UploadFile, File
from app.controllers.post.search_image_controller import search_image_controller
from app.schemas.vehicle_schemas import SearchResponse
from app.schemas.response import APIResponse
from app.routes.router import appRouter

@appRouter.post(
    "/search/image", response_model=APIResponse[SearchResponse]
)
async def search_by_image_endpoint(file: UploadFile = File(...)):
    """
    Endpoint para buscar imágenes parecidas proporcionando una imagen base.
    """
    return await search_image_controller(file)
