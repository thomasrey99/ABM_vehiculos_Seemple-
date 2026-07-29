from pydantic import BaseModel, ConfigDict, Field


class UpdateVehicleRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    license_plate: str | None = Field(
        default=None,
        min_length=6,
        max_length=15,
    )

    brand: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    model: str | None = Field(
        default=None,
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

    insurance_policy: str | None = Field(
        default=None,
        max_length=50,
    )

    observations: str | None = Field(
        default=None,
        max_length=2000,
    )

    is_active: bool | None = None