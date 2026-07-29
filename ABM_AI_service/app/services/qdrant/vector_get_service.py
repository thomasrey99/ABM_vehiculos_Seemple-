from app.db.qdrant_client import async_client


async def get_point_by_id(embedding_id: str, collection: str):
    """
    Recupera un punto puntual de Qdrant por su id (embedding_id).
    Devuelve None si no existe.
    """
    points = await async_client.retrieve(
        collection_name=collection,
        ids=[embedding_id],
        with_payload=True,
    )

    if not points:
        return None

    point = points[0]
    return {
        "vehicle_id": point.payload.get("vehicle_id"),
        "embedding_id": point.id,
        "label": point.payload.get("label"),
        "license_plate": point.payload.get("license_plate"),
        "payload": point.payload,
    }