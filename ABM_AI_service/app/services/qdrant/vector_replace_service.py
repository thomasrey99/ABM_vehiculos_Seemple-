from app.db.qdrant_client import async_client
from qdrant_client.models import PointStruct


async def replace_vector_embedding(embedding_id: str, new_embedding: list, collection: str):
    """
    Reemplaza el vector (embedding) de un punto ya existente, preservando su
    payload actual (vehicle_id, label, brand, model, color, license_plate,
    details). Devuelve None si el embedding_id no existe, para que el
    controller pueda responder 404 en vez de crear un punto nuevo "fantasma".
    """
    points = await async_client.retrieve(
        collection_name=collection,
        ids=[embedding_id],
        with_payload=True,
    )

    if not points:
        return None

    existing_payload = points[0].payload

    await async_client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=embedding_id,
                vector=new_embedding,
                payload=existing_payload,
            )
        ],
    )

    return {
        "vehicle_id": existing_payload.get("vehicle_id"),
        "embedding_id": embedding_id,
        "label": existing_payload.get("label"),
        "license_plate": existing_payload.get("license_plate"),
    }