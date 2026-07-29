from app.config.settings import settings
from app.exceptions.appExceptions import (
    BadRequestException,
    InternalServerException,
    NotFoundException,
)
from app.services.qdrant.vector_get_service import get_point_by_id
from app.services.qdrant.vector_delete_service import delete_points_by_ids
from app.utils.response import build_response


async def delete_embedding_controller(embedding_id: str):
    """
    Elimina un único embedding (imagen) por su id, sin afectar al resto de
    las imágenes del mismo vehículo. Devuelve 404 si el embedding_id no
    corresponde a ningún punto existente.
    """
    try:
        if not embedding_id:
            raise BadRequestException("embedding_id es requerido")

        existing = await get_point_by_id(embedding_id, settings.COLLECTION_NAME)

        if existing is None:
            raise NotFoundException(f"No se encontró ningún vector con id {embedding_id}")

        await delete_points_by_ids([embedding_id], settings.COLLECTION_NAME)

        return build_response(
            success=True,
            message=f"Embedding {embedding_id} eliminado correctamente",
            data={
                "vehicle_id": existing["vehicle_id"],
                "embedding_id": embedding_id,
            },
        )

    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(str(e))