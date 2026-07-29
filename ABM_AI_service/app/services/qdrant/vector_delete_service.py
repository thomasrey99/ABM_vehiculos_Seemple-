from app.db.qdrant_client import async_client
from qdrant_client.http import models


async def delete_vectors_by_id(vehicle_id: str, collection: str):
    """
    Elimina de Qdrant todos los puntos vectoriales que coincidan con un vehicle_id específico usando un filtro.
    """
    result = await async_client.delete(
        collection_name=collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="vehicle_id",
                        match=models.MatchValue(value=vehicle_id),
                    ),
                ]
            )
        ),
    )
    return result


async def delete_points_by_ids(point_ids: list, collection: str):
    """
    Elimina puntos puntuales de Qdrant a partir de una lista de sus IDs.
    Se usa para revertir (rollback) inserciones parciales cuando falla
    una ingesta de imágenes a mitad de lote.
    """
    if not point_ids:
        return None

    result = await async_client.delete(
        collection_name=collection,
        points_selector=models.PointIdsList(points=point_ids),
    )
    return result