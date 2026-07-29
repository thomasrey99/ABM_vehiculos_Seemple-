from pydantic import BaseModel
from typing import List, Optional

class UpdateLabelRequest(BaseModel):
    embedding_id: str
    new_label: str

class UpdateVehicleRequest(BaseModel):
    """
    Todos los campos son opcionales: solo se actualizan los que el cliente
    envíe explícitamente (PATCH parcial). Se aplican a TODAS las imágenes
    indexadas de ese vehicle_id.
    """
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    details: Optional[List[str]] = None
    license_plate: Optional[str] = None