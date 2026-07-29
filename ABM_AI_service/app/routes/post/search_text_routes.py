from fastapi import Form
from app.routes.router import appRouter
from app.controllers.post.search_text_controller import search_text_controller
from app.schemas.vehicle_schemas import SearchResponse
from app.schemas.response import APIResponse

@appRouter.post("/search/text", response_model=APIResponse[SearchResponse])
async def search_image_by_text_endpoint(text: str = Form(...)):
    """
    Endpoint donde el usuario envía un texto para recibir imágenes similares.
    """
    return await search_text_controller(text)
