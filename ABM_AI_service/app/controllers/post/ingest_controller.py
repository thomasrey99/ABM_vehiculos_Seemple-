import json
from pydantic import ValidationError

from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.schemas.request import IngestMetadata
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_save_service import save_labeled_vector
from app.services.qdrant.vector_delete_service import delete_points_by_ids
from app.utils.response import build_response


async def ingest_controller(metadata: str, files):
    """
    Recibe la metadata del vehículo + lista de imágenes como un único JSON
    (`metadata`), y los archivos correspondientes (`files`) en el mismo
    orden posicional que `metadata.images`. Cada imagen tiene un `label`
    (sector) y una lista de `details` (puede tener varios, o ninguno). La
    patente se recibe manualmente dentro de `metadata` — el ANPR NO se usa
    en la ingesta, es exclusivo de `/search/image`. Si falla una imagen a
    mitad del lote, revierte (rollback) las que ya se habían insertado.
    """
    try:
        raw_metadata = json.loads(metadata)
    except json.JSONDecodeError as e:
        raise BadRequestException(f"El campo 'metadata' no es un JSON válido: {str(e)}")

    try:
        data = IngestMetadata(**raw_metadata)
    except ValidationError as e:
        raise BadRequestException(f"metadata inválida: {e.errors()}")

    if not data.vehicle_id:
        raise BadRequestException("vehicle_id es requerido")

    if not data.license_plate or not data.license_plate.strip():
        raise BadRequestException("license_plate es requerido")

    if not data.images:
        raise BadRequestException("Se debe enviar al menos una imagen en 'images'")

    if len(data.images) != len(files):
        raise BadRequestException(
            f"La cantidad de imágenes en metadata ({len(data.images)}) no "
            f"coincide con la cantidad de archivos enviados ({len(files)})"
        )

    raw_images = [await file.read() for file in files]

    # Metadata COMPARTIDA por todas las imágenes de este vehículo.
    vehicle_metadata = {
        "license_plate": data.license_plate.strip().upper(),
        "brand": data.brand,
        "model": data.model,
        "color": data.color,
    }

    indexed_results = []
    inserted_point_ids = []

    try:
        for image_bytes, image_data in zip(raw_images, data.images):

            embedding = await generate_embedding(image_bytes)

            image_details = [d.strip() for d in image_data.details if d and d.strip()]

            point_id = await save_labeled_vector(
                data.vehicle_id,
                embedding,
                image_data.label,
                settings.COLLECTION_NAME,
                vehicle_metadata,
                image_details,
            )
            inserted_point_ids.append(point_id)

            indexed_results.append({
                "vehicle_id": str(data.vehicle_id),
                "embedding_id": point_id,
                "label": image_data.label,
                "license_plate": vehicle_metadata["license_plate"],
                "details": image_details,
            })

        return build_response(
            success=True,
            message=f"Imágenes indexadas correctamente para el vehiculo con id {data.vehicle_id}",
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
                    f"Puede haber vectores huérfanos para vehicle_id={data.vehicle_id}. Error original: {str(e)}"
                )
        raise InternalServerException(str(e))