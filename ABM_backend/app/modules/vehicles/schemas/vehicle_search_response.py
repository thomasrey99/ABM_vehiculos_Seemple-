from pydantic import BaseModel, ConfigDict, Field

from app.modules.vehicles.schemas.vehicle_response import VehicleResponse


class MatchedImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    score: float


class VehicleSearchMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle: VehicleResponse
    score: float
    matched_images: list[MatchedImageResponse] = Field(default_factory=list)


class VehicleSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    threshold: float | None = None
    matches: list[VehicleSearchMatchResponse] = Field(default_factory=list)