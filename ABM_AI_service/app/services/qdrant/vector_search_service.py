from app.db.qdrant_client import async_client
from qdrant_client.http import models
from typing import List, Optional, Union


def _point_to_dict(payload: dict, score: float) -> dict:
    return {
        "vehicle_id": payload.get("vehicle_id"),
        "label": payload.get("label"),
        "license_plate": payload.get("license_plate"),
        "brand": payload.get("brand"),
        "model": payload.get("model"),
        "color": payload.get("color"),
        "details": payload.get("details"),
        "score": score,
    }


async def search_vectors_by_embedding(
    embedding: list,
    collection: str,
    label_filter: Union[str, List[str]] = None,
    limit: int = 10,
    score_threshold: Optional[float] = 0.5,
):
    """
    Realiza una consulta en Qdrant enviando un vector y buscando los puntos
    más similares. `label_filter` es un filtro EXACTO y estricto por
    etiqueta (ej. "frente"), usado en /search/filtered.

    `score_threshold` es un piso ABSOLUTO de Qdrant: cualquier score por
    debajo se descarta antes de llegar al umbral dinámico. Tiene sentido
    para similitud imagen-imagen (scores altos, ~0.7-0.95), pero es
    demasiado agresivo para similitud texto-imagen (CLIP da scores mucho
    más bajos, ~0.2-0.4, aunque el match sea correcto). Para búsquedas de
    texto, pasar `score_threshold=None` para no aplicar ningún piso acá y
    dejar que `compute_dynamic_threshold` (sobre los resultados ya
    devueltos) haga todo el filtrado.
    """
    query_filter = None

    if label_filter:
        if isinstance(label_filter, list):
            match_condition = models.MatchAny(any=label_filter)
        else:
            match_condition = models.MatchValue(value=label_filter)

        query_filter = models.Filter(
            must=[models.FieldCondition(key="label", match=match_condition)]
        )

    response = await async_client.query_points(
        collection_name=collection,
        query=embedding,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
        score_threshold=score_threshold,
    )

    return [_point_to_dict(item.payload, item.score) for item in response.points]


async def search_vehicle_by_license_plate(license_plate: str, collection: str, limit: int = 50):
    """
    Busca directamente por coincidencia EXACTA de patente (sin similitud
    vectorial). Se usa cuando se detecta una patente con alta confianza en
    la imagen de búsqueda.
    """
    points, _ = await async_client.scroll(
        collection_name=collection,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="license_plate",
                    match=models.MatchValue(value=license_plate),
                )
            ]
        ),
        limit=limit,
        with_payload=True,
    )

    return [_point_to_dict(point.payload, 1.0) for point in points]