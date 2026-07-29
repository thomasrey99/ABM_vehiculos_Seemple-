from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicializa los recursos de la aplicación.
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Base de datos inicializada.")

    yield

    print("🛑 Aplicación detenida.")