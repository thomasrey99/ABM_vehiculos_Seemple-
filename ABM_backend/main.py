from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.lifespan import lifespan
from app.exceptions.app_exceptions import AppException
from app.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.router import router

app = FastAPI(
    title="Vehicle Management API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

app.add_exception_handler(AppException, app_exception_handler)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)