from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from sqlalchemy import DateTime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.image_label import ImageLabel
from app.enums.embedding_status import EmbeddingStatus
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.image_detail import ImageDetail
    from app.models.vehicle import Vehicle

class VehicleImage(BaseModel):
    __tablename__ = "vehicle_images"

    vehicle_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    label: Mapped[ImageLabel] = mapped_column(
        Enum(ImageLabel, name="image_label"),
        nullable=False,
    )

    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="images",
    )

    details: Mapped[list["ImageDetail"]] = relationship(
        "ImageDetail",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    embedding_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
        Enum(EmbeddingStatus, name="embedding_status"),
        default=EmbeddingStatus.PENDING,
        nullable=False,
    )

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )