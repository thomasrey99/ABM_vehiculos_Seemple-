from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.schemas.vehicle_schemas import SearchResponse
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_search_service import (
    search_vectors_by_embedding,
    search_vehicle_by_license_plate,
)
from app.utils.dynamic_threshold import compute_dynamic_threshold
from app.utils.group_results import group_matches_by_vehicle
from app.utils.plate_recognition import recognize_plate
from app.utils.response import build_response


async def search_image_controller(file):
    """
    Toma una imagen enviada por el cliente. Primero intenta identificar una
    patente en la imagen (ANPR, con confianza >= PLATE_MIN_CONFIDENCE); si
    la encuentra, busca el vehículo directamente por esa patente (match
    exacto, sin necesidad de comparar embeddings). Si no se detecta ninguna
    patente confiable, o no hay ningún vehículo indexado con esa patente,
    recurre a la búsqueda por similitud visual con umbral dinámico (como
    antes).
    """
    try:
        if not file:
            raise BadRequestException("file is required")

        image_bytes = await file.read()

        plate_result = recognize_plate(image_bytes)

        if plate_result:
            plate_matches = await search_vehicle_by_license_plate(
                plate_result["text"], settings.COLLECTION_NAME
            )

            if plate_matches:
                matches = group_matches_by_vehicle(plate_matches, threshold=0.0)
                return build_response(
                    success=True,
                    message=f"Vehículo encontrado por patente {plate_result['text']}",
                    data=SearchResponse(matches=matches, threshold=None),
                )
            # Se detectó una patente confiable pero no hay ningún vehículo
            # indexado con ella: seguimos con la búsqueda visual como
            # respaldo en vez de devolver un resultado vacío.

        embedding = await generate_embedding(image_bytes)
        results = await search_vectors_by_embedding(embedding, settings.COLLECTION_NAME)

        scores = [r["score"] for r in results]
        threshold = compute_dynamic_threshold(scores)
        matches = group_matches_by_vehicle(results, threshold)

        return build_response(
            success=True,
            message="Busqueda de imagen completada",
            data=SearchResponse(matches=matches, threshold=threshold),
        )

    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerException(str(e))