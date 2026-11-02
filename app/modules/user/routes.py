from fastapi import APIRouter

from app.core.response import success_response
from app.modules.auth.dependencies import CurrentUserDep, UserServiceDep
from app.modules.user.schemas import UserResponse, UserUpdateSchema

user_routes = APIRouter(prefix="/users", tags=["Users"])


@user_routes.get("")
async def me(current_user: CurrentUserDep):
    return success_response(data=UserResponse.from_user(current_user))


@user_routes.patch("")
async def update(
    user_service: UserServiceDep, user_id: CurrentUserDep, data: UserUpdateSchema
):
    result = await user_service.update_user(user_id=user_id.id, user_data=data)
    return success_response(data=result, message="User updated successfully")


@user_routes.delete("")
async def delete_my_account(user_service: UserServiceDep, current_user: CurrentUserDep):
    await user_service.delete_own_account(user=current_user)
    return success_response(message="Account deleted successfully")
