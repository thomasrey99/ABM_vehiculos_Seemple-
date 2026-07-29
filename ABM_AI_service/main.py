import os
import importlib
import pkgutil
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.init_db import init_qdrant
from app.exceptions.appExceptions import AppException
from app.exceptions.handlers import (
    app_exception_handler, 
    generic_exception_handler, 
    validation_exception_handler, 
    http_exception_handler
)
from app.routes.router import appRouter
from app import routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_qdrant()
    yield

app = FastAPI(lifespan=lifespan)

def load_routes(app_instance):
    """
    Carga recursivamente todos los archivos dentro de app/routes 
    para registrar los decoradores de rutas en appRouter.
    """
    routes_path = routes.__path__[0]
    
    for root, _, files in os.walk(routes_path):
        relative_path = os.path.relpath(root, routes_path)
        if relative_path == ".":
            package_prefix = "app.routes"
        else:
            package_prefix = f"app.routes.{relative_path.replace(os.sep, '.')}"
            
        for _, name, is_pkg in pkgutil.iter_modules([root], package_prefix + "."):
            if not is_pkg:
                importlib.import_module(name)
                print(f"Ruta cargada: {name}")

# 1. Carga todas las rutas automáticamente
load_routes(app)

# 2. Registro de handlers de excepciones
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# 3. Registro del enrutador
app.include_router(appRouter)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)