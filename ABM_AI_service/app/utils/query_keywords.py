import re
from typing import List

# Stopwords comunes en español/inglés y palabras genéricas del dominio que
# no aportan como filtro (vehiculo, auto, carro son redundantes siempre).
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "en", "con", "y", "o", "que", "para", "por", "es", "son", "the", "a",
    "an", "of", "and", "or", "in", "on", "with", "vehiculo", "vehículo",
    "auto", "autos", "carro", "carros", "coche", "coches",
}


def extract_keywords(text: str) -> List[str]:
    """
    Extrae palabras clave relevantes de una consulta en lenguaje natural
    (ej: "vehiculo marca toyota modelo corolla color blanco con rayon en
    puerta izquierda"), quitando stopwords y palabras muy cortas, para
    usarlas como filtro de coincidencia textual sobre los metadatos del
    vehículo (brand, model, color, details) en Qdrant.
    """
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]