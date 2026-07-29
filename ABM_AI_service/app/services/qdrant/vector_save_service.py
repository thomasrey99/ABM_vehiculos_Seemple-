from app.db.qdrant_client import async_client
from qdrant_client.models import PointStruct
from typing import List, Optional
from uuid import UUID
import uuid


async def save_labeled_vector(
    vehicle_id: UUID,
    embedding: list,
    label: str,
    collection: str,
    vehicle_metadata: Optional[dict] = None,
    image_details: Optional[List[str]] = None,
):
    """
    Guarda (hace un upsert) un nuevo vector numérico en la base de datos
    Qdrant. Guarda también datos asociados (payload):
    - `label` e `image_details`: específicos de ESTA imagen/sector
      (ej. label="atras", details=["rayón puerta izquierda"]).
    - `vehicle_metadata`: compartido por TODAS las imágenes del vehículo
      (brand, model, color, license_plate).
    """
    point_id = str(uuid.uuid4())

    payload = {
        "vehicle_id": str(vehicle_id),
        "label": label,
    }

    if image_details:
        payload["details"] = image_details

    if vehicle_metadata:
        for key, value in vehicle_metadata.items():
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