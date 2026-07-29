from fastapi import UploadFile, File, Form
from app.routes.router import appRouter
from typing import List, Optional
from app.controllers.post.filtered_search_image_controller import (
    filtered_search_image_controller,
)
from app.schemas.vehicle_schemas import SearchResponse
from app.schemas.response import APIResponse


@appRouter.post(
    "/search/filtered", response_model=APIResponse[SearchResponse]
)
async def search_filtered_image_endpoint(
    file: UploadFile = File(..., description="Imagen para búsqueda"),
    labels: Optional[List[str]] = Form(
        None, description="Etiquetas opocionales (ej: frente)"
    ),
):
    """
    Endpoint para búsqueda de imagen que acepta etiquetas extra para filtrar.
    """
    return await filtered_search_image_controller(file, labels)
