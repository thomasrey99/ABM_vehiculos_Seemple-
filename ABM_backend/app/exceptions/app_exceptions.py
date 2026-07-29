class AppException(Exception):
    """
    Excepción base de la aplicación.
    """

    def __init__(
        self,
        message: str,
        error: str,
        status_code: int,
    ):
        self.message = message
        self.error = error
        self.status_code = status_code


class BadRequestException(AppException):
    def __init__(
        self,
        message: str,
        error: str = "BAD_REQUEST",
    ):
        super().__init__(
            message=message,
            error=error,
            status_code=400,
        )


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "No autorizado.",
        error: str = "UNAUTHORIZED",
    ):
        super().__init__(
            message=message,
            error=error,
            status_code=401,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        message: str,
        error: str = "NOT_FOUND",
    ):
        super().__init__(
            message=message,
            error=error,
            status_code=404,
        )


class ConflictException(AppException):
    def __init__(
        self,
        message: str,
        error: str = "CONFLICT",
    ):
        super().__init__(
            message=message,
            error=error,
            status_code=409,
        )


class InternalServerException(AppException):
    def __init__(
        self,
        message: str = "Internal server error.",
        error: str = "INTERNAL_SERVER_ERROR",
    ):
        super().__init__(
            message=message,
            error=error,
            status_code=500,
        )