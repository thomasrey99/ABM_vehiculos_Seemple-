from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.api_key import verify_api_key
from app.modules.users.controller import UserController
from app.modules.users.dependencies import get_user_controller
from app.modules.users.schemas.create_request import CreateUserRequest
from app.modules.users.schemas.update_request import UpdateUserRequest


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("")
async def create_user(
    request: CreateUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.create(request)


@router.get("")
async def get_all_users(
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_all()


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: UUID,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_by_id(user_id)


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.update(
        user_id=user_id,
        request=request,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.delete(user_id)