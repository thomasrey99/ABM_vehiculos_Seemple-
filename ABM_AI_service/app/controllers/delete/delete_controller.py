from app.config.settings import settings
from app.exceptions.appExceptions import InternalServerException
from uuid import UUID

from app.services.qdrant.vector_delete_service import delete_vectors_by_id
from app.utils.response import build_response


async def delete_controller(vehicle_id: UUID):
    """
    Llama al servicio de borrado para eliminar todos los vectores de un vehículo y construye el formato de respuesta de éxito o error.
    """
    try:
        vehicle_id_str = str(vehicle_id)
        result = await delete_vectors_by_id(vehicle_id_str, settings.COLLECTION_NAME)
        return build_response(
            success=True,
            message=f"Se eliminaron las imagenes asociadas a la entidad con UUID {vehicle_id_str}",
            data=result,
        )
    except Exception as e:
        raise InternalServerException(str(e))
