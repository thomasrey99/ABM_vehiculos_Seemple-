from pydantic import BaseModel, ConfigDict

from app.enums.image_label import ImageLabel


class UpdateVehicleImageLabelRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    label: ImageLabel