from app.exceptions.app_exceptions import (
    ConflictException,
    NotFoundException,
)


class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(
            message="Usuario no encontrado.",
            error="USER_NOT_FOUND",
        )


class UserAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__(
            message="Ya existe un usuario con ese email.",
            error="USER_ALREADY_EXISTS",
        )