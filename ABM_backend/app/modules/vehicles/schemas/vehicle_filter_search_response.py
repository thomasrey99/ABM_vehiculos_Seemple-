from pydantic import BaseModel, ConfigDict, Field

from app.modules.vehicles.schemas.vehicle_filter_query import VehicleFilterQuery
from app.modules.vehicles.schemas.vehicle_summary_response import (
    VehicleSummaryResponse,
)


class VehicleFilterSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    applied_filters: VehicleFilterQuery
    # Puede devolver varios vehículos => versión liviana (ver
    # VehicleSummaryResponse). Para el detalle completo de uno puntual,
    # usar get_by_id con su `id`.
    vehicles: list[VehicleSummaryResponse] = Field(default_factory=list)