from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.role import Role


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: Role
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )