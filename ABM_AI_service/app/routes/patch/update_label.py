from fastapi import Body
from app.controllers.patch.patch_controller import update_label_controller
from app.schemas.request import UpdateLabelRequest
from app.schemas.response import APIResponse, IndexedImageResponse
from app.routes.router import appRouter

@appRouter.patch("/update-label", response_model=APIResponse[IndexedImageResponse])
async def update_label_endpoint(
    payload: UpdateLabelRequest=Body(...)
):
    """
    Actualiza la etiqueta de un vector en la base de datos Qdrant.
    """
    return await update_label_controller(payload.embedding_id, payload.new_label)