from deep_translator import GoogleTranslator
from app.exceptions.appExceptions import AppException


def translate_to_english(text: str) -> str:
    """
    Utiliza Google Translator para traducir consultas textuales desde cualquier idioma (auto-detectado) al inglés, mejorando la precisión del modelo.
    """
    try:
        translator = GoogleTranslator(source="auto", target="en")
        print(text)
        translated_text = translator.translate(text)
        print(translated_text)
        return translated_text

    except Exception as e:
        raise AppException(
            message="Error en el servicio de traducción", error=str(e), status_code=500
        )
