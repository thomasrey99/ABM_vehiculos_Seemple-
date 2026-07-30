from pydantic import BaseModel
from typing import List, Optional

class UpdateLabelRequest(BaseModel):
    embedding_id: str
    new_label: str

class UpdateVehicleRequest(BaseModel):
    """
    Todos los campos son opcionales: solo se actualizan los que el cliente
    envíe explícitamente (PATCH parcial). Se aplican a TODAS las imágenes
    indexadas de ese vehicle_id. `details` NO está acá: es un atributo por
    imagen — se actualiza junto al reemplazo de esa imagen puntual, no a
    nivel vehículo.
    """
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None

class ImageIngestData(BaseModel):
    """
    Una imagen a ingestar: su etiqueta de sector (UN solo label) y sus
    detalles (CERO o MÁS, ej. abolladura + vidrio roto en la misma foto).
    """
    label: str
    details: List[str] = []

class IngestMetadata(BaseModel):
    """
    Payload JSON completo de una ingesta: datos del vehículo (compartidos
    por todas sus imágenes) + la lista de imágenes con su label/details
    respectivos. El orden de `images` debe coincidir 1 a 1 con el orden de
    los archivos enviados en el campo `files` del form-data.
    """
    vehicle_id: str
    brand: str
    model: str
    color: str
    license_plate: str
    images: List[ImageIngestData]