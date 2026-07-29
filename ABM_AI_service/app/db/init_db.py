from qdrant_client.models import VectorParams, PayloadSchemaType
from app.config.settings import settings
from app.db.qdrant_client import sync_client as client


def init_qdrant():
    """
    Inicializa la base vectorial configurando la colección y creando índices
    para las búsquedas (vehicle_id, label, license_plate exactos; brand,
    model, color y details como texto libre) en caso de que no existan
    previamente.
    """
    collections = [settings.COLLECTION_NAME]

    for collection in collections:
        if not client.collection_exists(collection_name=collection):
            print(f"Creating collection: {collection}")
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(
                    size=settings.CLIP_VECTOR_SIZE, distance=settings.VECTOR_DISTANCE
                ),
            )
        else:
            print(f"La coleccion {collection} ya existe. Saltando la creacion.")

        client.create_payload_index(
            collection_name=collection,
            field_name="vehicle_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        client.create_payload_index(
            collection_name=collection,
            field_name="label",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        # Patente: coincidencia EXACTA (se usa para el lookup directo cuando
        # se detecta una patente con alta confianza en la imagen de búsqueda).
        client.create_payload_index(
            collection_name=collection,
            field_name="license_plate",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        # Marca/modelo/color/detalles: texto libre, para permitir búsquedas
        # semánticas híbridas (ej. "toyota corolla blanco con rayón").
        for text_field in ("brand", "model", "color", "details"):
            client.create_payload_index(
                collection_name=collection,
                field_name=text_field,
                field_schema=PayloadSchemaType.TEXT,
            )