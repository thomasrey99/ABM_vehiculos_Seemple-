from fastapi import APIRouter, Depends, Security, Form, File, UploadFile

from uuid import UUID

from app.dependencies.api_key import verify_api_key
from app.modules.vehicles.controller import VehicleController
from app.modules.vehicles.dependencies import (
    get_vehicle_controller,
)
from app.modules.vehicles.schemas.update_vehicle_image_label_request import (
    UpdateVehicleImageLabelRequest,
)
from app.modules.vehicles.schemas.update_vehicle_request import (
    UpdateVehicleRequest,
)


router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
    dependencies=[
        Security(verify_api_key),
    ],
)


@router.post("")
async def create_vehicle(
    request: str = Form(...),
    files: list[UploadFile] = File(...),
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.create(
        request=request,
        files=files,
    )

@router.post("/search/image")
async def search_vehicles_by_image(
    file: UploadFile = File(...),
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.search_by_image(file)

@router.post("/search/text")
async def search_vehicles_by_text(
    text: str = Form(...),
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.search_by_text(text)

@router.get("")
async def get_all_vehicles(
    controller: VehicleController = Depends(get_vehicle_controller)
):
    return await controller.get_all()

@router.get("/{vehicle_id}")
async def get_vehicle_by_id(
    vehicle_id: UUID,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    return await controller.get_by_id(vehicle_id)

@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: UUID,
    request: UpdateVehicleRequest,
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.update(vehicle_id, request)

@router.patch("/{vehicle_id}/images/{image_id}/label")
async def update_vehicle_image_label(
    vehicle_id: UUID,
    image_id: UUID,
    request: UpdateVehicleImageLabelRequest,
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.update_image_label(vehicle_id, image_id, request)

@router.patch("/{vehicle_id}/images/{image_id}/file")
async def replace_vehicle_image(
    vehicle_id: UUID,
    image_id: UUID,
    file: UploadFile = File(...),
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.replace_image(vehicle_id, image_id, file)

@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: UUID,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    return await controller.delete(vehicle_id)

@router.delete("/{vehicle_id}/images/{image_id}")
async def delete_vehicle_image(
    vehicle_id: UUID,
    image_id: UUID,
    controller: VehicleController = Depends(get_vehicle_controller),
):
    return await controller.delete_image(vehicle_id, image_id)