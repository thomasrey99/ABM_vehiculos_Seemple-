from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)

        return user

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.id == user_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.email == email)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def exists_by_email(
        self,
        email: str,
    ) -> bool:

        return (
            await self.get_by_email(email)
        ) is not None

    async def get_all(
        self,
    ) -> list[User]:

        stmt = (
            select(User)
            .order_by(User.created_at.desc())
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def update(
        self,
        user: User,
    ) -> User:

        updated_user = await self.db.merge(user)
        
        return updated_user

    async def delete(
        self,
        user: User,
    ) -> None:

        await self.db.delete(user)
