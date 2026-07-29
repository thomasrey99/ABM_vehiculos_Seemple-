from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.enums.image_detail import ImageDetailType
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.vehicle_image import VehicleImage

class ImageDetail(BaseModel):

    __tablename__="image_details"

    image_id:Mapped[UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicle_images.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    detail_type: Mapped[ImageDetailType]=mapped_column(
        Enum(ImageDetailType, name="image_detail_type"),
        nullable=False
    )   

    description: Mapped[str | None]=mapped_column(
        Text,
        nullable=True
    )

    image: Mapped["VehicleImage"] = relationship(
        back_populates="details"
    )