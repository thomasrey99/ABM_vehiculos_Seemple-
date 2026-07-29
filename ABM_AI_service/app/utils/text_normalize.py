import unicodedata


def normalize_text(text: str) -> str:
    """
    Normaliza texto para matching robusto: minúsculas y sin tildes/diacríticos
    (ej. "Rayón" -> "rayon", "GRIS" -> "gris"). Evita que una tilde de más o
    de menos entre lo que ingresa el cliente y lo que escribe quien busca
    rompa el matching de texto.
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))