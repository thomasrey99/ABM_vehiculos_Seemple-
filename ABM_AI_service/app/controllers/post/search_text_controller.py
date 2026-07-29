from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.schemas.vehicle_schemas import SearchResponse
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_search_service import search_vectors_by_embedding
from app.utils.dynamic_threshold import compute_dynamic_threshold
from app.utils.group_results import group_matches_by_vehicle
from app.utils.query_keywords import extract_keywords
from app.utils.response import build_response


async def search_text_controller(text: str):
    """
    Toma un texto en lenguaje natural (ej: "vehiculo marca toyota modelo
    corolla color blanco con rayon en puerta izquierda"). Combina dos
    señales:
    1. Palabras clave extraídas del texto original, usadas como filtro de
       texto libre (OR) sobre brand/model/color/details en Qdrant, para
       priorizar vehículos cuyos metadatos coincidan explícitamente.
    2. El embedding CLIP del texto (traducido al inglés), para similitud
       visual-semántica dentro de ese conjunto.
    Luego calcula un umbral dinámico de aceptación y devuelve los vehículos
    agrupados que lo superan.
    """
    try:
        if not text or not text.strip():
            raise BadRequestException("Se requiere un texto para realizar la búsqueda")

        # Las keywords se extraen del texto ORIGINAL (antes de traducir),
        # ya que brand/model/color/details se guardan tal como los ingresó
        # el cliente en la ingesta.
        keywords = extract_keywords(text)

        embedding = await generate_embedding(text)

        results = await search_vectors_by_embedding(
            embedding, settings.COLLECTION_NAME, keyword_filter=keywords
        )

        scores = [r["score"] for r in results]
        threshold = compute_dynamic_threshold(scores)

        matches = group_matches_by_vehicle(results, threshold)

        return build_response(
            success=True,
            message=f"Busqueda para '{text}' realizada con éxito",
            data=SearchResponse(matches=matches, threshold=threshold),
        )
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerException(str(e))