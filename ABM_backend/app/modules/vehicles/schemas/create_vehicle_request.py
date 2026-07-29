from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.enums.image_detail import ImageDetailType
from app.enums.image_label import ImageLabel


class CreateImageDetailRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    detail_type: ImageDetailType

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class CreateVehicleImageRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    filename: str = Field(
        min_length=1,
        max_length=255,
    )

    label: ImageLabel

    details: list[CreateImageDetailRequest] = Field(
        default_factory=list,
    )


class CreateVehicleRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    owner_id: UUID

    license_plate: str = Field(
        min_length=5,
        max_length=15,
    )

    brand: str = Field(
        min_length=1,
        max_length=50,
    )

    model: str = Field(
        min_length=1,
        max_length=50,
    )

    color: str | None = Field(
        default=None,
        max_length=50,
    )

    year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )

    observations: str | None = Field(
        default=None,
        max_length=2000,
    )

    images: list[CreateVehicleImageRequest] = Field(
        min_length=1,
    )
