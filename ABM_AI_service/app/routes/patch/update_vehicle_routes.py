from fastapi import Body, Path
from app.routes.router import appRouter
from app.controllers.patch.update_vehicle_controller import update_vehicle_controller
from app.schemas.request import UpdateVehicleRequest
from app.schemas.response import APIResponse


@appRouter.patch("/vehicles/{vehicle_id}", response_model=APIResponse[dict])
async def update_vehicle_endpoint(
    vehicle_id: str = Path(..., description="UUID del vehículo a actualizar"),
    payload: UpdateVehicleRequest = Body(...),
):
    """
    Actualiza brand/model/color/details/license_plate en todas las imágenes
    indexadas de un vehículo. Solo se modifican los campos enviados
    explícitamente en el body (PATCH parcial).
    """
    return await update_vehicle_controller(vehicle_id, payload)