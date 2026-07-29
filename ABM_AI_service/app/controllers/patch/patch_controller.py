from app.config.settings import settings
from app.exceptions.appExceptions import (
    BadRequestException,
    InternalServerException,
    NotFoundException,
)
from app.services.qdrant.update_label import update_label
from app.utils.response import build_response


async def update_label_controller(embedding_id: str, new_label: str):
    """
    Actualiza la etiqueta de un vector en la base de datos Qdrant.
    """
    try:
        collection_name = settings.COLLECTION_NAME

        if not embedding_id:
            raise BadRequestException(
                "Se debe enviar el UUID del vector y el valor de la nueva etiqueta"
            )

        if not new_label or not new_label.strip():
            raise BadRequestException("La nueva etiqueta no puede estar vacía")

        response = await update_label(embedding_id, new_label, collection_name)

        if response is None:
            raise NotFoundException(
                f"No se encontró ningún vector con id {embedding_id}"
            )

        return build_response(
            success=True,
            message=f"Etiqueta actualizada correctamente para el vector {embedding_id}",
            data=response,
        )

    except (BadRequestException, NotFoundException):
        raise
    except Exception as e:
        raise InternalServerException(str(e))