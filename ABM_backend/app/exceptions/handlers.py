from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.app_exceptions import AppException
from app.shared.response import error_response


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            error=exc.error,
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content=error_response(
            message="Error de validación.",
            error="VALIDATION_ERROR",
            data=exc.errors(),
        ),
    )


async def http_exception_handler(
    request: Request,
    
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            error="HTTP_EXCEPTION",
        ),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Error interno del servidor.",
            error="INTERNAL_SERVER_ERROR",
        ),
    )