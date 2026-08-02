import base64
import json

from fastapi import UploadFile
from openai import AsyncOpenAI

from app.core.logging import logger
from app.core.settings import settings
from app.enums.image_detail import ImageDetailType
from app.services.damage_detection.damage_detection_service import (
    DamageDetectionService,
)
from app.services.damage_detection.models.detected_damage import DetectedDamage

_SYSTEM_PROMPT = (
    "Sos un inspector experto en daños de carrocería de vehículos. "
    "Analizás UNA foto puntual y detectás únicamente los daños VISIBLES "
    "Y EVIDENTES en esa imagen (no inventes daños que no se vean con "
    "claridad, y no repitas el mismo daño con dos tipos distintos).\n\n"
    "REGLA CRÍTICA DE ORIENTACIÓN: cuando menciones 'izquierda' o "
    "'derecha' en la descripción de un daño, usá SIEMPRE la convención "
    "estándar de la industria automotriz: la perspectiva de un "
    "conductor sentado al volante, mirando hacia adelante (hacia el "
    "frente del vehículo). NUNCA uses la perspectiva de un espectador "
    "parado frente a la foto mirando el auto — esa perspectiva queda "
    "INVERTIDA respecto de la del conductor y es la fuente más común de "
    "error. Si te indican el sector fotografiado (label) de la imagen, "
    "usalo como ancla: es un dato confiable sobre qué lateral del "
    "vehículo estás viendo, incluso si en tu campo visual la carrocería "
    "'apunta' hacia el lado contrario.\n\n"
    "Para cada daño, elegí el tipo más preciso de la lista permitida y "
    "agregá una descripción breve (máx. 15 palabras) indicando su "
    "ubicación dentro de esa imagen (ej. 'puerta delantera', 'panel "
    "trasero', 'paragolpe'), sin necesidad de repetir izquierda/derecha "
    "si el sector ya lo deja claro. Si la foto no muestra ningún daño, "
    "devolvé una lista vacía."
)

_DAMAGE_SCHEMA = {
    "name": "vehicle_damage_report",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "damages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "detail_type": {
                            "type": "string",
                            "enum": [item.value for item in ImageDetailType],
                        },
                        "description": {"type": "string"},
                    },
                    "required": ["detail_type", "description"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["damages"],
        "additionalProperties": False,
    },
}


class OpenAIDamageDetectionService(DamageDetectionService):

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def detect_damages(
        self,
        file: UploadFile,
        label: str | None = None,
    ) -> list[DetectedDamage]:
        await file.seek(0)
        image_bytes = await file.read()
        await file.seek(0)  # se re-usa después para subir a Cloud Storage

        if not image_bytes:
            return []

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"

        user_text = "Detectá los daños visibles en esta imagen del vehículo."

        if label:
            user_text += (
                f" El sector fotografiado en esta imagen es: '{label}'. "
                f"Usá este dato como referencia de orientación real del "
                f"vehículo (no de tu campo visual) al describir la "
                f"ubicación de cada daño."
            )

        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_DAMAGE_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": _DAMAGE_SCHEMA,
                },
                temperature=0,
            )

            parsed = json.loads(response.choices[0].message.content)

            damages: list[DetectedDamage] = []

            for item in parsed.get("damages", []):
                try:
                    detail_type = ImageDetailType(item["detail_type"])
                except (KeyError, ValueError):
                    continue

                damages.append(
                    DetectedDamage(
                        detail_type=detail_type.value,
                        description=item.get("description"),
                    )
                )

            return damages

        except Exception:
            logger.exception(
                "Falló la detección automática de daños vía OpenAI para "
                "el archivo '%s' (label='%s'). Se continúa sin daños "
                "detectados.",
                file.filename,
                label,
            )
            return []