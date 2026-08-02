from pydantic import BaseModel, ConfigDict, Field


class VehicleFilterSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=500)