from fastapi import APIRouter

from app.modules.vehicles.routes import router as vehicles_router

router = APIRouter()


router.include_router(vehicles_router)