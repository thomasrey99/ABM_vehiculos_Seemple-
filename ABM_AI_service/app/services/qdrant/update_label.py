from app.db.qdrant_client import async_client
from app.config.settings import settings

async def update_label(embedding_id: str, new_label: str, collection: str):
    """
    Actualiza la etiqueta de un vector en la base de datos Qdrant 
    y retorna el objeto mapeado para el modelo de respuesta.
    """
    await async_client.set_payload(
            collection_name=collection,
            payload={"label": new_label},
            points=[embedding_id]
    )

    points = await async_client.retrieve(
        collection_name=collection,
        ids=[embedding_id],
        with_payload=True
    )


    if points:
        point = points[0]
        return {
            "vehicle_id": point.payload.get("vehicle_id"),
            "embedding_id": point.id,
            "label": point.payload.get("label")
        }
    
    return None
