from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.vehicle_image import VehicleImage

class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    license_plate: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        index=True,
        nullable=False,
    )

    brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    insurance_policy: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    observations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    images: Mapped[list["VehicleImage"]] = relationship(
        "VehicleImage",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="VehicleImage.created_at"
    )