from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.vehicles.controller import VehicleController
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.service import VehicleService
from app.services.recognition.ai_recognition_service import (
    AIRecognitionService,
)
from app.services.storage.google_cloud_storage_service import (
    GoogleCloudStorageService,
)

def get_vehicle_service(
    db: AsyncSession = Depends(get_db),
) -> VehicleService:

    return VehicleService(
        db=db,
        vehicle_repository=VehicleRepository(db),
        storage_service=GoogleCloudStorageService(),
        recognition_service=AIRecognitionService(),
    )


def get_vehicle_controller(
    service: VehicleService = Depends(get_vehicle_service),
) -> VehicleController:

    return VehicleController(service)