from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums.role import Role


class CreateUserRequest(BaseModel):
    """
    Schema utilizado para crear un usuario.
    """

    first_name: str = Field(
        min_length=2,
        max_length=100,
        description="Nombre del usuario.",
        examples=["Juan"],
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
        description="Apellido del usuario.",
        examples=["Pérez"],
    )

    email: EmailStr = Field(
        description="Correo electrónico.",
        examples=["juan@email.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=100,
        description="Contraseña del usuario.",
        examples=["Password123"],
    )

    role: Role = Field(
        default=Role.CLIENT,
        description="Rol del usuario.",
        examples=["CLIENT"],
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )