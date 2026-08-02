from pydantic import BaseModel, ConfigDict, Field

from app.modules.vehicles.schemas.vehicle_filter_query import VehicleFilterQuery
from app.modules.vehicles.schemas.vehicle_response import VehicleResponse


class VehicleFilterSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    applied_filters: VehicleFilterQuery
    vehicles: list[VehicleResponse] = Field(default_factory=list)