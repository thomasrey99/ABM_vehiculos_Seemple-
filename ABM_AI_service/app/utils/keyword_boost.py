from typing import List

from app.utils.text_normalize import normalize_text

# Puntos adicionales por cada palabra clave de la consulta que aparece
# explícitamente en los metadatos estructurados del vehículo. Es un boost
# ADITIVO, no un filtro: un vehículo sin ningún match textual sigue
# pudiendo aparecer si su similitud visual es alta, solo que sin el extra.
BOOST_PER_KEYWORD_MATCH = 0.08


def compute_keyword_boost(result: dict, keywords: List[str]) -> float:
    """
    Calcula un puntaje adicional según cuántas palabras clave de la consulta
    en lenguaje natural aparecen en los metadatos de ESTA imagen puntual:
    brand/model/color (compartidos por el vehículo) + label y details
    (específicos del sector fotografiado en esta imagen). Por eso el boost
    se calcula por resultado individual, ANTES de agrupar por vehículo: así
    "rayón en puerta izquierda" prioriza justo la imagen cuyo label o
    details mencionan "izquierda", no cualquier imagen del mismo vehículo.
    Tanto las keywords como los metadatos se normalizan (sin tildes) antes
    de compararse.
    """
    if not keywords:
        return 0.0

    searchable_parts = [
        normalize_text(str(result.get(field)))
        for field in ("brand", "model", "color", "label")
        if result.get(field)
    ]
    searchable_parts.extend(
        normalize_text(str(d)) for d in (result.get("details") or [])
    )

    searchable_text = " ".join(searchable_parts)

    matches = sum(1 for keyword in keywords if keyword in searchable_text)
    return matches * BOOST_PER_KEYWORD_MATCH