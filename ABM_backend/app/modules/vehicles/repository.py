from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vehicle import Vehicle
from app.models.vehicle_image import VehicleImage


class VehicleRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:

        self.db.add(vehicle)

        await self.db.flush()

        await self.db.refresh(vehicle)

        return vehicle

    async def get_by_id(
        self,
        vehicle_id: UUID,
    ) -> Vehicle | None:

        stmt = (
            select(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .options(
                selectinload(Vehicle.images).selectinload(
                    VehicleImage.details
                ),
            )
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_license_plate(
        self,
        license_plate: str,
    ) -> Vehicle | None:

        stmt = (
            select(Vehicle)
            .where(
                Vehicle.license_plate == license_plate
            )
            .options(
                selectinload(Vehicle.images).selectinload(
                    VehicleImage.details
                ),
            )
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[Vehicle]:

        stmt = (
            select(Vehicle)
            .options(
                selectinload(Vehicle.images).selectinload(
                    VehicleImage.details
                ),
            )
            .order_by(Vehicle.created_at.desc())
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def delete(
        self,
        vehicle: Vehicle,
    ) -> None:

        await self.db.delete(vehicle)
        
    async def update(
        self,
        vehicle: Vehicle,
    ) -> Vehicle:

        await self.db.flush()

        await self.db.refresh(vehicle)

        return vehicle