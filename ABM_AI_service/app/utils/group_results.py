from collections import defaultdict
from typing import List
from uuid import UUID

from app.schemas.vehicle_schemas import VehiclesGroup, ImageMatch


def group_matches_by_vehicle(results: list, threshold: float) -> List[VehiclesGroup]:
    """
    Agrupa los resultados devueltos por Qdrant (uno por imagen/vector) en
    entidades por vehicle_id. `label` y `details` quedan dentro de cada
    ImageMatch (son atributos de ESA imagen/sector puntual); brand/model/
    color/license_plate quedan a nivel del vehículo (compartidos por todas
    sus imágenes). Filtra por el umbral de aceptación indicado.
    """
    grouped = defaultdict(list)
    vehicle_metadata = {}

    for r in results:
        if r["score"] < threshold:
            continue

        vid = r.get("vehicle_id")
        if not vid:
            continue

        grouped[vid].append(
            ImageMatch(score=r["score"], label=r.get("label"), details=r.get("details"))
        )

        if vid not in vehicle_metadata:
            vehicle_metadata[vid] = {
                "license_plate": r.get("license_plate"),
                "brand": r.get("brand"),
                "model": r.get("model"),
                "color": r.get("color"),
            }

    return [
        VehiclesGroup(
            vehicle_id=UUID(vid),
            images=imgs,
            **vehicle_metadata.get(vid, {}),
        )
        for vid, imgs in grouped.items()
    ]