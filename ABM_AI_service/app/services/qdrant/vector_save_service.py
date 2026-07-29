from app.db.qdrant_client import async_client
from qdrant_client.models import PointStruct
from typing import Optional
from uuid import UUID
import uuid


async def save_labeled_vector(
    vehicle_id: UUID,
    embedding: list,
    label: str,
    collection: str,
    vehicle_metadata: Optional[dict] = None,
):
    """
    Guarda (hace un upsert) un nuevo vector numérico en la base de datos
    Qdrant. Guarda también datos asociados (payload) como el ID del
    vehículo, la etiqueta descriptiva, y opcionalmente los metadatos del
    vehículo (license_plate, brand, model, color, details).
    """
    print(vehicle_metadata)
    point_id = str(uuid.uuid4())

    payload = {
        "vehicle_id": str(vehicle_id),
        "label": label,
    }

    if vehicle_metadata:
        for key, value in vehicle_metadata.items():
            # No pisamos el payload con valores vacíos (ej. patente no
            # detectada, o listas de detalles vacías).
            if value not in (None, "", []):
                payload[key] = value

    await async_client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        ]
    )

    return point_id