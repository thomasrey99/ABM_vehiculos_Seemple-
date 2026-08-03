from uuid import UUID
from fastapi import UploadFile
from app.modules.vehicles.schemas.vehicle_filter_search_response import (
    VehicleFilterSearchResponse,
)
from app.modules.vehicles.schemas.create_vehicle_request import (
    CreateVehicleRequest,
)
from app.modules.vehicles.schemas.update_vehicle_image_label_request import (
    UpdateVehicleImageLabelRequest,
)
from app.modules.vehicles.schemas.update_vehicle_request import (
    UpdateVehicleRequest,
)
from app.modules.vehicles.service import VehicleService
from app.shared.response import success_response

class VehicleController:

    def __init__(
        self,
        service: VehicleService,
    ):
        self.service = service

    async def create(
        self,
        request: str,
        files: list[UploadFile],
    ):

        create_request = CreateVehicleRequest.model_validate_json(
            request
        )

        vehicle = await self.service.create(
            request=create_request,
            files=files,
        )

        return success_response(
            data=vehicle,
            message="Vehículo creado correctamente.",
        )

    async def get_by_id(
        self,
        vehicle_id: UUID,
    ):

        vehicle = await self.service.get_by_id(
            vehicle_id
        )

        return success_response(
            data=vehicle,
            message="Vehículo obtenido correctamente."
        )

    async def get_all(
        self,
    ):

        vehicles = await self.service.get_all()

        return success_response(
            data=vehicles,
            message="Vehículos obtenidos correctamente."
        )
        
    async def get_by_license_plate(
        self,
        license_plate: str,
    ):

        vehicle = await self.service.get_by_license_plate(
            license_plate
        )

        return success_response(
            data=vehicle,
            message="Vehículo obtenido correctamente."
        )

    async def update(
        self,
        vehicle_id: UUID,
        request: UpdateVehicleRequest,
    ):

        vehicle = await self.service.update(
            vehicle_id=vehicle_id,
            request=request,
        )

        return success_response(
            data=vehicle,
            message="Vehículo actualizado correctamente.",
        )
        
    

    async def update_image_label(
        self,
        vehicle_id: UUID,
        image_id: UUID,
        request: UpdateVehicleImageLabelRequest,
    ):

        vehicle = await self.service.update_image_label(
            vehicle_id=vehicle_id,
            image_id=image_id,
            request=request,
        )

        return success_response(
            data=vehicle,
            message="Label de la imagen actualizado correctamente.",
        )

    async def replace_image(
        self,
        vehicle_id: UUID,
        image_id: UUID,
        file: UploadFile,
    ):

        vehicle = await self.service.replace_image(
            vehicle_id=vehicle_id,
            image_id=image_id,
            file=file,
        )

        return success_response(
            data=vehicle,
            message="Imagen reemplazada correctamente.",
        )

    async def delete(
        self,
        vehicle_id: UUID
    ):
        await self.service.delete(vehicle_id)

        return success_response(
            message="Vehiculo eliminado correctamente.",
        )

    async def delete_image(
        self,
        vehicle_id: UUID,
        image_id: UUID,
    ):

        await self.service.delete_image(
            vehicle_id=vehicle_id,
            image_id=image_id,
        )

        return success_response(
            message="Imagen eliminada correctamente.",
        )

    async def search_by_image(
        self,
        file: UploadFile,
    ):
        result = await self.service.search_by_image(file)

        return success_response(
            data=result.model_dump(mode="json"),
            message="Búsqueda por imagen completada.",
        )

    async def search_by_text(
        self,
        text: str,
    ):
        result = await self.service.search_by_text(text)

        return success_response(
            data=result.model_dump(mode="json"),
            message="Búsqueda por texto completada.",
        )
        
    async def search_by_filters(
        self,
        text: str,
    ):
        filters, vehicles = await self.service.search_by_filters(text)

        response = VehicleFilterSearchResponse(
            applied_filters=filters,
            vehicles=vehicles,
        )

        return success_response(
            data=response.model_dump(mode="json"),
            message="Búsqueda por filtros completada.",
        )