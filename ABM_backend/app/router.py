from fastapi import APIRouter


from app.modules.users.routes import router as users_router
from app.modules.vehicles.routes import router as vehicles_router
router = APIRouter()

router.include_router(users_router)
router.include_router(vehicles_router)