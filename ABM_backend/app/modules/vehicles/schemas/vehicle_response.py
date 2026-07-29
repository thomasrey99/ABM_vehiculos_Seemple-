from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.embedding_status import EmbeddingStatus
from app.enums.image_detail import ImageDetailType
from app.enums.image_label import ImageLabel


class ImageDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    detail_type: ImageDetailType
    description: str | None


class VehicleImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    image_url: str
    label: ImageLabel
    embedding_status: EmbeddingStatus

    details: list[ImageDetailResponse] = Field(
        default_factory=list
    )


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    license_plate: str

    brand: str

    model: str

    color: str | None

    year: int | None

    insurance_policy: str | None

    observations: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    images: list[VehicleImageResponse] = Field(
        default_factory=list
    )