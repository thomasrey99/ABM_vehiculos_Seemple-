from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.users.controller import UserController
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:

    return UserService(
        db=db,
        repository=UserRepository(db),
    )


def get_user_controller(
    service: UserService = Depends(get_user_service),
) -> UserController:

    return UserController(service)