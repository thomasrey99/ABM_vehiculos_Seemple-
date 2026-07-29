from app.config.settings import settings
from app.exceptions.appExceptions import BadRequestException, InternalServerException
from app.schemas.vehicle_schemas import SearchResponse
from app.services.embedding.embedding_service import generate_embedding
from app.services.qdrant.vector_search_service import search_vectors_by_embedding
from app.utils.dynamic_threshold import compute_dynamic_threshold
from app.utils.group_results import group_matches_by_vehicle
from app.utils.keyword_boost import compute_keyword_boost
from app.utils.query_keywords import extract_keywords
from app.utils.response import build_response


async def search_text_controller(text: str):
    """
    Toma un texto en lenguaje natural (ej: "auto marca fiat modelo siena
    color gris con abolladura en la puerta derecha") y combina dos señales:

    1. Similitud visual-semántica: el embedding CLIP del texto (traducido
       al inglés) comparado contra los embeddings de las imágenes, SIN un
       piso de score duro (ese piso tiene sentido para imagen-imagen, no
       para texto-imagen, donde los scores son naturalmente más bajos).
    2. Coincidencia textual: un boost aditivo de puntaje por cada palabra
       clave de la consulta que aparece en brand/model/color/details del
       vehículo, para priorizar a quien matchea explícitamente la
       descripción sin descartar de plano a quien no.

    El umbral dinámico se calcula sobre los scores YA combinados (visual +
    boost), así que sigue siendo relativo a la distribución real de esta
    búsqueda puntual.
    """
    try:
        if not text or not text.strip():
            raise BadRequestException("Se requiere un texto para realizar la búsqueda")

        # Las keywords se extraen del texto ORIGINAL (antes de traducir),
        # ya que brand/model/color/details se guardan tal como los ingresó
        # el cliente en la ingesta.
        keywords = extract_keywords(text)

        embedding = await generate_embedding(text)

        # Traemos un pool más amplio de candidatos y SIN piso de score duro
        # (score_threshold=None), porque acá el score es texto-vs-imagen y
        # el umbral dinámico de más abajo ya se encarga de discriminar.
        results = await search_vectors_by_embedding(
            embedding,
            settings.COLLECTION_NAME,
            limit=30,
            score_threshold=None,
        )

        for result in results:
            result["score"] += compute_keyword_boost(result, keywords)

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