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
    keyword_filter: Optional[List[str]] = None,
    limit: int = 10,
    score_threshold: float = 0.5,
):
    """
    Realiza una consulta en Qdrant enviando un vector y buscando los puntos
    más similares. Permite opcionalmente:
    - `label_filter`: filtro EXACTO y estricto por etiqueta (ej. "frente").
    - `keyword_filter`: lista de palabras clave para un filtro de texto
      libre (OR) sobre brand/model/color/details, usado en la búsqueda
      semántica híbrida por texto.

    `score_threshold` actúa solo como un piso muy laxo para descartar ruido
    evidente antes de llegar a Qdrant; el filtrado fino de relevancia lo
    hace `compute_dynamic_threshold` sobre los resultados ya devueltos.
    """
    must_conditions = []
    should_conditions = []

    if label_filter:
        if isinstance(label_filter, list):
            match_condition = models.MatchAny(any=label_filter)
        else:
            match_condition = models.MatchValue(value=label_filter)

        must_conditions.append(
            models.FieldCondition(key="label", match=match_condition)
        )

    if keyword_filter:
        for keyword in keyword_filter:
            for field in ("brand", "model", "color", "details"):
                should_conditions.append(
                    models.FieldCondition(key=field, match=models.MatchText(text=keyword))
                )

    query_filter = None
    if must_conditions or should_conditions:
        query_filter = models.Filter(
            must=must_conditions or None,
            should=should_conditions or None,
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
    vectorial). Se usa cuando se detecta una patente con alta confianza
    (>= PLATE_MIN_CONFIDENCE) en la imagen de búsqueda: en ese caso no hace
    falta comparar embeddings, se puede resolver la entidad directamente
    por el índice de patente.
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