from app.config.settings import settings
from app.exceptions.appExceptions import (
    BadRequestException,
    InternalServerException,
    NotFoundException,
)
from app.schemas.request import UpdateVehicleRequest
from app.services.qdrant.vector_update_metadata_service import update_vehicle_metadata
from app.utils.response import build_response


async def update_vehicle_controller(vehicle_id: str, payload: UpdateVehicleRequest):
    """
    Actualiza parcialmente los metadatos de un vehículo (brand/model/color/
    details/license_plate) en TODAS sus imágenes indexadas. Solo se
    modifican los campos que el cliente envió explícitamente (PATCH
    parcial real, vía exclude_unset).
    """
    try:
        if not vehicle_id:
            raise BadRequestException("vehicle_id es requerido")

        metadata = {
            key: value
            for key, value in payload.model_dump(exclude_unset=True).items()
            if value not in (None, "", [])
        }

        if not metadata:
            raise BadRequestException("Se debe enviar al menos un campo para actualizar")

        updated_count = await update_vehicle_metadata(
            vehicle_id, metadata, settings.COLLECTION_NAME
        )

        if updated_count == 0:
            raise NotFoundException(f"No se encontró ningún vehículo con id {vehicle_id}")

        return build_response(
            success=True,
            message=f"Metadatos actualizados en {updated_count} imagen(es) del vehículo {vehicle_id}",
            data={
                "vehicle_id": str(vehicle_id),
                "updated_images": updated_count,
                "updated_fields": metadata,
            },
        )

    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(str(e))