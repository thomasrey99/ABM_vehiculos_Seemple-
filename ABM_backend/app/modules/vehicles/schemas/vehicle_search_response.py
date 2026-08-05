from pydantic import BaseModel, ConfigDict, Field

from app.modules.vehicles.schemas.vehicle_summary_response import (
    VehicleSummaryResponse,
)


class MatchedImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    score: float
    details: list[str] = Field(default_factory=list)


class VehicleSearchMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Varios matches por búsqueda => datos livianos del vehículo. Si se
    # necesita el detalle completo (imágenes, etc.), usar el endpoint
    # get_by_id con el `id` que viene acá.
    vehicle: VehicleSummaryResponse
    score: float
    matched_images: list[MatchedImageResponse] = Field(default_factory=list)


class VehicleSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    threshold: float | None = None
    matches: list[VehicleSearchMatchResponse] = Field(default_factory=list)