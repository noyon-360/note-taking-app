from beanie import PydanticObjectId
from fastapi import APIRouter

from app.common.pagination import PaginationDep
from app.core.response import build_metadata, success_response
from app.modules.auth.dependencies import CurrentUserDep, UserServiceDep
from app.modules.user.schemas import (
    UserPostsResponse,
    UserResponse,
    UserUpdateSchema,
)

user_routes = APIRouter(prefix="/users", tags=["Users"])


@user_routes.get("")
async def me(current_user: CurrentUserDep):
    return success_response(data=UserResponse.model_validate(current_user))


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


@user_routes.get("/{user_id}/posts")
async def user_posts(
    user_id: PydanticObjectId,
    pagination: PaginationDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    result = await user_service.get_user_posts(
        user_id=user_id, skip=pagination.skip, limit=pagination.limit
    )
    return success_response(
        data=UserPostsResponse.model_validate(result),
        metadata=build_metadata(
            page=pagination.page, limit=pagination.limit, total=result["total"]
        ),
    )
