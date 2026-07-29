from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

class IndexedImageResponse(BaseModel):
    vehicle_id: str
    embedding_id: str
    label: str
    license_plate: Optional[str] = None