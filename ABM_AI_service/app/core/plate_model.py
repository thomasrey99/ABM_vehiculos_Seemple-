from fast_alpr import ALPR
from app.config.settings import settings

_plate_model: ALPR | None = None


def get_plate_model() -> ALPR:
    """
    Devuelve la instancia única del modelo ANPR (fast-alpr), cargándolo
    recién en el primer uso (lazy loading) en vez de al importar el
    módulo. Mismo motivo que model_embedding.get_model(): no bloquear el
    arranque del servidor.
    """
    global _plate_model
    if _plate_model is None:
        _plate_model = ALPR(
            detector_model=settings.PLATE_DETECTOR_MODEL,
            ocr_model=settings.PLATE_OCR_MODEL,
        )
    return _plate_model