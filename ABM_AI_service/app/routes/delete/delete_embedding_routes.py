from fastapi import Path
from app.routes.router import appRouter
from app.controllers.delete.delete_embedding_controller import delete_embedding_controller
from app.schemas.response import APIResponse


@appRouter.delete("/delete/embedding/{embedding_id}", response_model=APIResponse[dict])
async def delete_embedding_endpoint(
    embedding_id: str = Path(..., description="El ID del embedding/imagen a eliminar"),
):
    """
    Elimina un único embedding (imagen) por su id, sin afectar al resto de
    las imágenes del mismo vehículo.
    """
    return await delete_embedding_controller(embedding_id)