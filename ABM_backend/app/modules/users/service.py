from uuid import UUID

from app.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)

from app.models.user import User

from app.modules.users.repository import UserRepository

from app.modules.users.schemas.create_request import CreateUserRequest
from app.modules.users.schemas.update_request import UpdateUserRequest


class UserService:

    def __init__(
        self,
        db: AsyncSession,
        repository: UserRepository,
    ):

        self.repository = repository
        self.db = db



    async def create(
        self,
        request: CreateUserRequest,
    ) -> User:

        if await self.repository.exists_by_email(request.email):
            raise UserAlreadyExistsException()

        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password_hash=hash_password(request.password),
            role=request.role,
            is_active=True,
        )

        user_created = await self.repository.create(user)

        await self.db.commit()
        await self.db.refresh(user_created)

        return user_created



    async def get_all(
        self,
    ) -> list[User]:
        """
        Obtiene todos los usuarios registrados.
        """

        return await self.repository.get_all()



    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User:
        """
        Busca un usuario por su UUID.

        Si no existe devuelve una excepción
        de negocio.
        """


        user = await self.repository.get_by_id(user_id)


        if user is None:
            raise UserNotFoundException()


        return user

    async def update(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
    ) -> User:
        """
        Actualiza un usuario existente.
        """
        user = await self.get_by_id(user_id)

        if (
            request.email is not None
            and request.email != user.email
            and await self.repository.exists_by_email(request.email)
        ):
            raise UserAlreadyExistsException()

        # Actualización de campos opcionales
        if request.first_name is not None:
            user.first_name = request.first_name

        if request.last_name is not None:
            user.last_name = request.last_name

        if request.email is not None:
            user.email = request.email

        if request.password is not None:
            user.password_hash = hash_password(request.password)

        if request.role is not None:
            user.role = request.role

        if request.is_active is not None:
            user.is_active = request.is_active

        # Delegamos al repositorio la actualización
        updated_user = await self.repository.update(user)
        
        # Hacemos commit y refresh para persistir los cambios
        await self.db.commit()
        await self.db.refresh(updated_user)

        return updated_user

    async def delete(
        self,
        user_id: UUID,
    ) -> None:

        user = await self.get_by_id(user_id)

        await self.repository.delete(user)
        
        await self.db.commit()