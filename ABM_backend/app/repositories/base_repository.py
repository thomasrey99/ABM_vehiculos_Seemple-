from typing import Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Repositorio base con operaciones CRUD comunes.
    """

    def __init__(
        self,
        model: Type[ModelType],
        session: AsyncSession,
    ):
        self.model = model
        self.session = session

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)

        await self.session.commit()
        await self.session.refresh(entity)

        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.commit()
        await self.session.refresh(entity)

        return entity

    async def get_by_id(self, entity_id: UUID) -> ModelType | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model)
        )

        return list(result.scalars().all())

    async def delete(self, entity: ModelType) -> None:
        await self.session.delete(entity)
        await self.session.commit()