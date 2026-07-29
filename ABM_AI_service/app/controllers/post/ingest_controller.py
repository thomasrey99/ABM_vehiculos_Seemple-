from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_save_service import save_labeled_vector
from app.services.qdrant.vector_delete_service import delete_points_by_ids
from app.utils.response import build_response


async def ingest_controller(vehicle_id, files, labels, license_plate, brand, model, color, details=None):
    """
    Recibe un conjunto de imágenes y etiquetas de un vehículo, junto con sus
    metadatos (patente, marca, modelo, color, detalles) provistos por el
    backend, e indexa cada imagen en Qdrant con todos esos datos en el
    payload. La patente ya no se detecta por ANPR acá: la manda el backend,
    que ya la tiene validada como dato propio del vehículo.
    Si falla una imagen a mitad del lote, revierte (rollback) las que ya se
    habían insertado para no dejar datos parciales/huérfanos en Qdrant.
    """
    
    if not vehicle_id:
        raise BadRequestException("vehicle_id es requerido")

    if not license_plate:
        raise BadRequestException("license_plate es requerido")

    if len(files) != len(labels):
        raise BadRequestException("La cantidad de archivos y etiquetas no coincide")

    raw_images = [await file.read() for file in files]

    vehicle_metadata = {
        "license_plate": license_plate,
        "brand": brand,
        "model": model,
        "color": color,
        "details": details or [],
    }

    indexed_results = []
    inserted_point_ids = []

    try:
        for image_bytes, label in zip(raw_images, labels):

            embedding = await generate_embedding(image_bytes)

            point_id = await save_labeled_vector(
                vehicle_id, embedding, label, settings.COLLECTION_NAME, vehicle_metadata
            )
            inserted_point_ids.append(point_id)

            indexed_results.append({
                "vehicle_id": str(vehicle_id),
                "embedding_id": point_id,
                "label": label,
                "license_plate": license_plate,
            })

        return build_response(
            success=True,
            message=f"Imágenes indexadas correctamente para el vehiculo con id {vehicle_id}",
            data=indexed_results
        )

    except BadRequestException:
        raise
    except Exception as e:
        # Rollback: revertimos los vectores que ya se habían insertado en
        # este lote antes de que ocurriera el fallo.
        if inserted_point_ids:
            try:
                await delete_points_by_ids(inserted_point_ids, settings.COLLECTION_NAME)
            except Exception:
                raise InternalServerException(
                    f"Error indexando imágenes y el rollback también falló. "
                    f"Puede haber vectores huérfanos para vehicle_id={vehicle_id}. Error original: {str(e)}"
                )
        raise InternalServerException(str(e))