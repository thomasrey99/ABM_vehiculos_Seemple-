class AppException(Exception):
    def __init__(self, message: str, error: str=None, status_code: int=400):
        self.message = message
        self.error = error
        self.status_code = status_code


class BadRequestException(AppException):
    def __init__(self, message: str, error: str = "BAD_REQUEST"):
        super().__init__(message, error, 400)


class InternalServerException(AppException):
    def __init__(self, message: str, error: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(message, error, 500)


class NotFoundException(AppException):
    def __init__(self, message: str, error: str = "NOT_FOUND"):
        super().__init__(message, error, 404)