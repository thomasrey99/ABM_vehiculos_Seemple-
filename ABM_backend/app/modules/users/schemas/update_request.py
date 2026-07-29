from pydantic import BaseModel, EmailStr, Field

from app.enums.role import Role


class UpdateUserRequest(BaseModel):
    """
    Schema utilizado para actualizar un usuario existente.

    Todos los campos son opcionales porque el endpoint
    permite actualizar parcialmente el usuario.
    """

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nuevo nombre del usuario.",
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nuevo apellido del usuario.",
    )

    email: EmailStr | None = Field(
        default=None,
        description="Nuevo correo electrónico.",
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=72,
        description="Nueva contraseña del usuario.",
    )

    role: Role | None = Field(
        default=None,
        description="Nuevo rol del usuario.",
    )

    is_active: bool | None = Field(
        default=None,
        description="Estado activo del usuario.",
    )