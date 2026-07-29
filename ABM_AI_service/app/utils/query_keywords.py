import re
from typing import List

from app.utils.text_normalize import normalize_text

# Stopwords comunes en español/inglés, palabras genéricas del dominio, y los
# nombres de los propios campos (marca/modelo/color) que el usuario suele
# mencionar en la oración pero que nunca van a coincidir literalmente con un
# valor real (ej. "marca" no es una marca). Ya están sin tildes porque las
# palabras extraídas se normalizan antes de compararlas contra este set.
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "en", "con", "y", "o", "que", "para", "por", "es", "son", "the", "a",
    "an", "of", "and", "or", "in", "on", "with", "vehiculo", "auto", "autos",
    "carro", "carros", "coche", "coches", "marca", "modelo", "color",
}


def extract_keywords(text: str) -> List[str]:
    """
    Extrae palabras clave relevantes de una consulta en lenguaje natural
    (ej: "auto marca fiat modelo siena color gris con abolladura en la
    puerta derecha"), normalizando tildes, quitando stopwords y palabras
    muy cortas. Se usan como boost de coincidencia textual sobre los
    metadatos del vehículo (brand, model, color, details) en la búsqueda
    híbrida, nunca como filtro excluyente.
    """
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
    normalized = [normalize_text(w) for w in words]
    return [w for w in normalized if w not in STOPWORDS and len(w) > 2]