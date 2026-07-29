from app.db.qdrant_client import async_client
from qdrant_client.http import models


async def update_vehicle_metadata(vehicle_id: str, metadata: dict, collection: str) -> int:
    """
    Actualiza los metadatos (brand/model/color/details/license_plate) de
    TODOS los puntos asociados a un vehicle_id, en una sola operación
    (filtro + set_payload), sin necesidad de iterar punto por punto.

    Devuelve la cantidad de puntos afectados (0 si no existía ningún punto
    con ese vehicle_id, para que el controller pueda responder 404).
    """
    vehicle_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="vehicle_id",
                match=models.MatchValue(value=str(vehicle_id)),
            )
        ]
    )

    count_result = await async_client.count(
        collection_name=collection,
        count_filter=vehicle_filter,
        exact=True,
    )

    if count_result.count == 0:
        return 0

    await async_client.set_payload(
        collection_name=collection,
        payload=metadata,
        points=models.FilterSelector(filter=vehicle_filter),
    )

    return count_result.count