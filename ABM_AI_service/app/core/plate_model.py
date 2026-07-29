from fast_alpr import ALPR
from app.config.settings import settings

# Instancia única del modelo ANPR, cargada una sola vez al importar el
# módulo (mismo patrón que app/core/model_embedding.py para CLIP).
plate_model = ALPR(
    detector_model=settings.PLATE_DETECTOR_MODEL,
    ocr_model=settings.PLATE_OCR_MODEL,
)