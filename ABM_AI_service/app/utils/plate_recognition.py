import cv2
import numpy as np
from typing import Optional, TypedDict

from app.core.plate_model import plate_model
from app.config.settings import settings


class PlateResult(TypedDict):
    text: str
    confidence: float


def _extract_confidence(ocr_confidence) -> float:
    """
    El campo de confianza del OCR puede venir como un único float o como
    una lista de floats (uno por carácter, según el modelo de OCR usado
    por fast-alpr). Se normaliza siempre a un único valor promedio.
    """
    if isinstance(ocr_confidence, (list, tuple)):
        if not ocr_confidence:
            return 0.0
        return sum(ocr_confidence) / len(ocr_confidence)
    return float(ocr_confidence or 0.0)


def recognize_plate(image_bytes: bytes, min_confidence: float = None) -> Optional[PlateResult]:
    """
    Detecta y lee una patente en una imagen CRUDA (sin el preprocesamiento
    de CLIP, que la reescala a 224x224 y destruiría la legibilidad de los
    caracteres). Devuelve None si no se detecta ninguna patente o si la
    confianza de la lectura no supera el umbral mínimo requerido
    (por defecto, settings.PLATE_MIN_CONFIDENCE = 0.90).
    """
    threshold = min_confidence if min_confidence is not None else settings.PLATE_MIN_CONFIDENCE

    try:
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # BGR, formato esperado por fast-alpr

        if image is None:
            return None

        results = plate_model.predict(image)

        best_text = None
        best_confidence = 0.0

        for result in results:
            if not result.ocr or not result.ocr.text:
                continue

            confidence = _extract_confidence(result.ocr.confidence)

            if confidence > best_confidence:
                best_confidence = confidence
                best_text = result.ocr.text.strip().upper()

        if best_text and best_confidence >= threshold:
            return {"text": best_text, "confidence": best_confidence}

        return None

    except Exception:
        # Si el reconocimiento de patente falla por cualquier motivo (imagen
        # corrupta, modelo no cargado, etc.) no debe interrumpir el flujo
        # principal de ingesta/búsqueda: simplemente no se detectó patente.
        return None