from app.core.model_embedding import model
from app.exceptions.appExceptions import AppException
from PIL import UnidentifiedImageError


from app.utils.preprocess_image import preprocess_image
from app.utils.traduction import translate_to_english


async def generate_embedding(input_data):
    """
    Toma como entrada texto o una imagen. Si es texto, lo traduce al inglés; si es imagen, la preprocesa. Luego, utiliza el modelo SentenceTransformer para convertir esa entrada en un vector numérico (embedding).
    """

    try:
        data_to_encode = None

        if isinstance(input_data, str):
            if not input_data.strip():
                raise AppException(
                    message="El texto de búsqueda no puede estar vacío",
                    error="EMPTY_TEXT",
                    status_code=400,
                )

            data_to_encode = translate_to_english(input_data)

        else:
            if hasattr(input_data, "read"):
                image_bytes = await input_data.read()
            else:
                # Ya viene como bytes crudos (ej. leídos una vez en el
                # controller para reusarlos también en el reconocimiento
                # de patente, sin consumir el stream del UploadFile dos veces).
                image_bytes = input_data

            if not image_bytes:
                raise AppException(
                    message="Archivo vacío", error="EMPTY_FILE", status_code=400
                )

            try:
                data_to_encode = preprocess_image(image_bytes)
            except UnidentifiedImageError:
                raise AppException(
                    message="El archivo no es una imagen válida",
                    error="INVALID_IMAGE",
                    status_code=400,
                )

        embedding = model.encode([data_to_encode])[0]

        if embedding is None or len(embedding) == 0:
            raise AppException(
                message="No se pudo generar el embedding",
                error="EMBEDDING_ERROR",
                status_code=500,
            )

        return embedding.tolist()

    except AppException:
        raise
    except Exception as e:
        raise AppException(
            message="Error interno generando embedding", error=str(e), status_code=500
        )