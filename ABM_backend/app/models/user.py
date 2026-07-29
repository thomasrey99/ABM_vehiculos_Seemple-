from app.enums.role import Role
from app.models.base_model import BaseModel
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.vehicle import Vehicle

class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    role: Mapped[Role]=mapped_column(
        Enum(Role, name="user_role"),
        default=Role.CLIENT,
        nullable=False
    )

    is_active: Mapped[bool]=mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    vehicles: Mapped[list["Vehicle"]]= relationship(
        "Vehicle",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
