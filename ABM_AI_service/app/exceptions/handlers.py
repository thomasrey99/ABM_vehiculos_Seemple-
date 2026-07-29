from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)
from app.exceptions.appExceptions import AppException
from app.utils.response import build_response


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            success=False, message=exc.message, data=None, error=exc.error
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = []
    for error in exc.errors():
        campo = error["loc"][-1] if len(error["loc"]) > 0 else "desconocido"
        errores.append(f"Falta el campo requerido: '{campo}'")

    mensaje_amigable = (
        " ".join(errores) if errores else "Error de validación en la petición"
    )

    return JSONResponse(
        status_code=400,
        content=build_response(
            success=False,
            message=mensaje_amigable,
            data=None,
            error="VALIDATION_ERROR",
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=build_response(
                success=False,
                message="La ruta o recurso solicitado no existe",
                data=None,
                error="NOT_FOUND",
            ),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            success=False,
            message=str(exc.detail),
            data=None,
            error=f"HTTP_{exc.status_code}_ERROR",
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_response(
            success=False,
            message="Unexpected error",
            data=None,
            error="Internal server error",
        ),
    )
