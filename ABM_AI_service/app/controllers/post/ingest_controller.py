from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_save_service import save_labeled_vector
from app.services.qdrant.vector_delete_service import delete_points_by_ids
from app.utils.plate_recognition import recognize_plate
from app.utils.response import build_response


async def ingest_controller(vehicle_id, files, labels, brand, model, color, details=None):
    """
    Recibe un conjunto de imágenes y etiquetas de un vehículo, junto con sus
    metadatos compartidos (marca, modelo, color) y un detalle específico POR
    IMAGEN (ej. un rayón asociado al sector "atras", no al vehículo entero).
    Detecta automáticamente la patente en el lote de imágenes (ANPR) e
    indexa cada imagen en Qdrant. Si falla una imagen a mitad del lote,
    revierte (rollback) las que ya se habían insertado.
    """
    if not vehicle_id:
        raise BadRequestException("vehicle_id es requerido")

    if len(files) != len(labels):
        raise BadRequestException("La cantidad de archivos y etiquetas no coincide")

    if details:
        if len(details) != len(files):
            raise BadRequestException(
                "Si se envían 'details', debe haber uno por cada imagen "
                "(enviar cadena vacía para las que no tengan detalle)"
            )
    else:
        details = [""] * len(files)

    # Leemos los bytes crudos de cada imagen una sola vez: se usan tanto
    # para el reconocimiento de patente (sin reescalar, para no perder
    # legibilidad de los caracteres) como para generar el embedding CLIP.
    raw_images = [await file.read() for file in files]

    detected_plate = None
    best_confidence = 0.0
    for image_bytes in raw_images:
        plate_result = recognize_plate(image_bytes)
        if plate_result and plate_result["confidence"] > best_confidence:
            detected_plate = plate_result["text"]
            best_confidence = plate_result["confidence"]

    # Metadata COMPARTIDA por todas las imágenes de este vehículo.
    vehicle_metadata = {
        "license_plate": detected_plate,
        "brand": brand,
        "model": model,
        "color": color,
    }

    indexed_results = []
    inserted_point_ids = []

    try:
        for image_bytes, label, detail in zip(raw_images, labels, details):

            embedding = await generate_embedding(image_bytes)

            # `details` es POR IMAGEN: solo se asocia al sector fotografiado
            # en esta foto puntual, no se replica a las demás.
            image_details = [detail.strip()] if detail and detail.strip() else []

            point_id = await save_labeled_vector(
                vehicle_id,
                embedding,
                label,
                settings.COLLECTION_NAME,
                vehicle_metadata,
                image_details,
            )
            inserted_point_ids.append(point_id)

            indexed_results.append({
                "vehicle_id": str(vehicle_id),
                "embedding_id": point_id,
                "label": label,
                "license_plate": detected_plate,
            })

        return build_response(
            success=True,
            message=f"Imágenes indexadas correctamente para el vehiculo con id {vehicle_id}",
            data=indexed_results
        )

    except BadRequestException:
        raise
    except Exception as e:
        if inserted_point_ids:
            try:
                await delete_points_by_ids(inserted_point_ids, settings.COLLECTION_NAME)
            except Exception:
                raise InternalServerException(
                    f"Error indexando imágenes y el rollback también falló. "
                    f"Puede haber vectores huérfanos para vehicle_id={vehicle_id}. Error original: {str(e)}"
                )
        raise InternalServerException(str(e))