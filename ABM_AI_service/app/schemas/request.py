from pydantic import BaseModel
from typing import Optional

class UpdateLabelRequest(BaseModel):
    embedding_id: str
    new_label: str

class UpdateVehicleRequest(BaseModel):
    """
    Todos los campos son opcionales: solo se actualizan los que el cliente
    envíe explícitamente (PATCH parcial). Se aplican a TODAS las imágenes
    indexadas de ese vehicle_id. `details` NO está acá: es un atributo por
    imagen/sector (ej. el rayón está "en la puerta izquierda"), no del
    vehículo completo — se actualiza junto al reemplazo de esa imagen
    puntual, no a nivel vehículo.
    """
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None