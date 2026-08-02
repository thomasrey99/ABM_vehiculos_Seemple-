from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.services.damage_detection.models.detected_damage import DetectedDamage


class DamageDetectionService(ABC):

    @abstractmethod
    async def detect_damages(
        self,
        file: UploadFile,
        label: str | None = None,
    ) -> list[DetectedDamage]:
        """
        Analiza UNA imagen de vehículo y devuelve los daños visibles
        detectados automáticamente, cada uno con su ImageDetailType y una
        breve descripción. Devuelve lista vacía si no detecta daños o si
        la detección falla.

        `label` es el sector fotografiado (ej. "lateral izquierda",
        "atras"), tal como lo indicó el cliente al ingestar la imagen. Se
        usa como ancla de orientación: sin este dato, el modelo de visión
        tiende a describir izquierda/derecha desde la perspectiva de quien
        mira la foto (el espectador) en vez de la convención automotriz
        estándar (el conductor sentado mirando hacia adelante), lo que
        produce descripciones invertidas cuando la cámara está ubicada
        frente a un lateral del vehículo.
        """
        ...