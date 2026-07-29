from uuid import UUID

from app.modules.users.schemas.create_request import CreateUserRequest
from app.modules.users.schemas.response import UserResponse
from app.modules.users.schemas.update_request import UpdateUserRequest
from app.modules.users.service import UserService
from app.shared.response import success_response


class UserController:
    """
    Controlador encargado de coordinar las peticiones del módulo de usuarios.
    """

    def __init__(
        self,
        service: UserService,
    ):
        self.service = service

    async def create(
        self,
        request: CreateUserRequest,
    ):
        user = await self.service.create(request)

        return success_response(
            message="Usuario creado correctamente.",
            data=UserResponse.model_validate(user).model_dump(mode="json"),
        )

    async def get_all(self):
        users = await self.service.get_all()

        return success_response(
            data=[
                UserResponse.model_validate(user).model_dump(mode="json")
                for user in users
            ]
        )

    async def get_by_id(
        self,
        user_id: UUID,
    ):
        user = await self.service.get_by_id(user_id)

        return success_response(
            data=UserResponse.model_validate(user).model_dump(mode="json"),
        )

    async def update(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
    ):
        user = await self.service.update(
            user_id=user_id,
            request=request,
        )

        return success_response(
            message="Usuario actualizado correctamente.",
            data=UserResponse.model_validate(user).model_dump(mode="json"),
        )

    async def delete(
        self,
        user_id: UUID,
    ):
        await self.service.delete(user_id)

        return success_response(
            message="Usuario eliminado correctamente.",
        )