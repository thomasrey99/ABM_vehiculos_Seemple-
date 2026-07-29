from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle_image import VehicleImage
    
class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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

    observations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="vehicles",
    )

    images: Mapped[list["VehicleImage"]] = relationship(
        "VehicleImage",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="VehicleImage.created_at"
    )