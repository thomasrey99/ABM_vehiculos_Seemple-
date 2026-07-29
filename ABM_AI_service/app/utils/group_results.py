from collections import defaultdict
from typing import List
from uuid import UUID

from app.schemas.vehicle_schemas import VehiclesGroup, ImageMatch


def group_matches_by_vehicle(results: list, threshold: float) -> List[VehiclesGroup]:
    """
    Agrupa los resultados devueltos por Qdrant (uno por imagen/vector) en
    entidades por vehicle_id, adjuntando los metadatos del vehículo
    (patente, marca, modelo, color, detalles) y filtrando por el umbral
    de aceptación indicado. Antes esta lógica estaba duplicada en los 3
    controllers de búsqueda; ahora vive en un solo lugar.
    """
    grouped = defaultdict(list)
    vehicle_metadata = {}

    for r in results:
        if r["score"] < threshold:
            continue

        vid = r.get("vehicle_id")
        if not vid:
            continue

        grouped[vid].append(ImageMatch(score=r["score"], label=r.get("label")))

        if vid not in vehicle_metadata:
            vehicle_metadata[vid] = {
                "license_plate": r.get("license_plate"),
                "brand": r.get("brand"),
                "model": r.get("model"),
                "color": r.get("color"),
                "details": r.get("details"),
            }

    return [
        VehiclesGroup(
            vehicle_id=UUID(vid),
            images=imgs,
            **vehicle_metadata.get(vid, {}),
        )
        for vid, imgs in grouped.items()
    ]