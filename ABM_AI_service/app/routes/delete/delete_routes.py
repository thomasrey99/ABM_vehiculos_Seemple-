from app.routes.router import appRouter
from typing import Any
from fastapi import Path
from uuid import UUID
from app.controllers.delete.delete_controller import delete_controller
from app.schemas.response import APIResponse

@appRouter.delete("/delete/{vehicle_id}", response_model=APIResponse[Any])
async def delete_vectors_endpoint(
    vehicle_id: UUID = Path(
        ..., description="El ID del vehiculo cuyas imagenes se quiere eliminar"
    ),
):
    """
    Endpoint para borrar toda la información vectorial de un vehiculo.
    """
    return await delete_controller(vehicle_id)
