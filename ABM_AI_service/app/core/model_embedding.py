from sentence_transformers import SentenceTransformer
from app.config.settings import settings

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """
    Devuelve la instancia única del modelo CLIP, cargándolo recién en el
    primer uso (lazy loading) en vez de al importar el módulo. Evita que
    la carga/descarga del modelo bloquee el arranque del servidor durante
    `load_routes()`, que es lo que hacía fallar el healthcheck de
    deployment (la app no llegaba a "application startup complete" a
    tiempo).
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.MODEL)
    return _model