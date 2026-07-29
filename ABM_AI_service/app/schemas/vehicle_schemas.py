from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ImageMatch(BaseModel):
    score: float
    label: Optional[str] = None

class VehiclesGroup(BaseModel):
    vehicle_id: UUID
    images: List[ImageMatch]
    license_plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    details: Optional[List[str]] = None

class SearchResponse(BaseModel):
    matches: List[VehiclesGroup]
    threshold: Optional[float] = None