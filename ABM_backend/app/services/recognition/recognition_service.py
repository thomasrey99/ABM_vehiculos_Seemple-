from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import UploadFile

from app.services.recognition.models.image_search_result import (
    ImageSearchResult,
)


class RecognitionService(ABC):

    @abstractmethod
    async def index_images(
        self,
        vehicle_id: UUID,
        license_plate: str,
        brand: str,
        model: str,
        color: str,
        images: list[tuple[UploadFile, str, list[str]]],
    ) -> list[str | None]:
        """
        Envía las imágenes al servicio de reconocimiento para su indexación,
        junto con los metadatos del vehículo (license_plate, brand, model,
        color). La patente ya no la detecta el servicio de IA por ANPR en
        este endpoint: la provee el backend.

        `images` es una lista de tuplas (archivo, label, details) EN EL
        ORDEN en que deben quedar asociadas en el `metadata.images` que
        espera el servicio de IA. `details` es la lista de detail_type de
        ESA imagen puntual (no del vehículo completo).

        Devuelve una lista de embedding_id (o None si esa imagen no pudo
        indexarse) EN EL MISMO ORDEN que la lista de entrada.
        """
        ...

    @abstractmethod
    async def search_by_image(
        self,
        file: UploadFile,
    ) -> ImageSearchResult:
        """
        Busca coincidencias visuales para la imagen dada.
        """
        ...

    @abstractmethod
    async def delete_by_id(
        self,
        vehicle_id: UUID,
    ) -> None:
        """
        Elimina todos los vectores asociados a un vehicle_id en el
        servicio de reconocimiento (Qdrant).
        """
        ...
    
    @abstractmethod
    async def update_vehicle_metadata(
        self,
        vehicle_id: UUID,
        fields: dict[str, str],
    ) -> int:
        """
        Actualiza los metadatos compartidos (brand/model/color/
        license_plate) de todas las imágenes indexadas de un vehículo.
        `fields` contiene únicamente los campos que cambiaron. Devuelve
        la cantidad de imágenes actualizadas en el servicio de
        reconocimiento.
        """
        ...
        
    @abstractmethod
    async def update_label(
        self,
        embedding_id: str,
        new_label: str,
    ) -> None:
        """
        Actualiza el label (sector fotografiado) de una imagen ya
        indexada en el servicio de reconocimiento.
        """
        ...
        
    @abstractmethod
    async def replace_image(
        self,
        embedding_id: str,
        file: UploadFile,
    ) -> None:
        """
        Reemplaza la imagen (y por lo tanto el embedding) de un punto ya
        indexado, conservando el resto de sus metadatos (vehicle_id,
        label, brand, model, color, license_plate, details). No vuelve a
        correr ANPR sobre la nueva imagen.
        """
        ...