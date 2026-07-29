from typing import List, Optional
from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.schemas.vehicle_schemas import SearchResponse
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_search_service import search_vectors_by_embedding
from app.utils.dynamic_threshold import compute_dynamic_threshold
from app.utils.group_results import group_matches_by_vehicle
from app.utils.response import build_response


async def filtered_search_image_controller(file, labels: Optional[List[str]] = None):
    """
    Genera el embedding de una imagen y busca en Qdrant aplicando estrictamente
    un filtrado por etiquetas (ej: buscar solo imágenes frontales), luego
    devuelve los vehículos agrupados (con sus metadatos) que superan el
    umbral de coincidencias.
    """
    try:
        if not file:
            raise BadRequestException("La imagen es requerida para la búsqueda.")

        embedding = await generate_embedding(file)

        if not labels:
            labels = ["frente", "frente 45 izquierda", "frente 45 derecha", "atras", "atras 45 izquierda", "atras 45 derecha"]

        results = await search_vectors_by_embedding(
            embedding=embedding,
            collection=settings.COLLECTION_NAME,
            label_filter=labels,
            limit=30,
        )

        scores = [r["score"] for r in results]
        threshold = compute_dynamic_threshold(scores)

        matches = group_matches_by_vehicle(results, threshold)[:10]

        return build_response(
            success=True,
            message="Búsqueda filtrada completada con éxito",
            data=SearchResponse(matches=matches, threshold=threshold),
        )

    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerException(str(e))