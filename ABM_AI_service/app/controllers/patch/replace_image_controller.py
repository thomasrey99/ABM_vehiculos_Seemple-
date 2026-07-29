from app.config.settings import settings
from app.exceptions.appExceptions import (
    BadRequestException,
    InternalServerException,
    NotFoundException,
)
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_replace_service import replace_vector_embedding
from app.schemas.response import IndexedImageResponse
from app.utils.response import build_response


async def replace_image_controller(embedding_id: str, file):
    """
    Reemplaza la imagen (y por lo tanto el embedding) de un punto ya
    indexado, identificado por su embedding_id. Conserva el resto del
    payload (vehicle_id, label, brand, model, color, license_plate,
    details) sin cambios.
    """
    try:
        if not embedding_id:
            raise BadRequestException("Se debe enviar el embedding_id del punto a reemplazar")

        if not file:
            raise BadRequestException("La nueva imagen es requerida")

        image_bytes = await file.read()
        embedding = await generate_embedding(image_bytes)

        result = await replace_vector_embedding(
            embedding_id, embedding, settings.COLLECTION_NAME
        )

        if result is None:
            raise NotFoundException(f"No se encontró ningún vector con id {embedding_id}")

        return build_response(
            success=True,
            message=f"Imagen reemplazada correctamente para el vector {embedding_id}",
            data=IndexedImageResponse(**result),
        )

    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(str(e))