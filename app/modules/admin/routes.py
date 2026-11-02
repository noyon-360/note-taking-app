from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from app.common.pagination import PaginationDep
from app.core.response import build_metadata, success_response
from app.modules.auth.dependencies import (
    AdminUserDep,
    AuthServiceDep,
    UserServiceDep,
    require_admin,
)
from app.modules.auth.schemas import RegisterSchema
from app.modules.note.dependencies import NoteServiceDep
from app.modules.user.models import User
from app.modules.user.schemas import UserRoleUpdateSchema

admin_routes = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)]
)


@admin_routes.get("/notes", description="All the User Notes")
async def get_all_notes(pageination: PaginationDep, note_service: NoteServiceDep):
    notes, total = await note_service.list_all_notes(
        pageination.skip, pageination.limit
    )
    return success_response(
        data=notes,
        message="All notes fetched successfully",
        metadata=build_metadata(pageination.page, pageination.limit, total),
    )


@admin_routes.post("/user", description="Create user by admin")
async def create_user(data: RegisterSchema, auth_service: AuthServiceDep):
    result = await auth_service.register(data)
    return success_response(
        data=result,
        message="User create successfully",
        status_code=status.HTTP_201_CREATED,
    )


@admin_routes.get("/users", description="All the users")
async def get_users(user_service: UserServiceDep, pageination: PaginationDep) -> User:
    users, total = await user_service.list_users(
        skip=pageination.skip, limit=pageination.limit
    )
    return success_response(
        data=users,
        message="All users fetched successfully",
        metadata=build_metadata(
            page=pageination.page, limit=pageination.limit, total=total
        ),
    )


@admin_routes.get("/users/{user_id}", description="Fetch user by id")
async def user_by_id(user_id: PydanticObjectId, user_service: UserServiceDep) -> User:
    user = await user_service.get_user_by_id(user_id=user_id)
    return success_response(
        data=user,
        message="User fetched successfully",
        status_code=status.HTTP_200_OK,
    )


@admin_routes.patch("/user/{user_id}/role", description="Admin Change a user's role")
async def update_user_role(
    user_service: UserServiceDep,
    admin: AdminUserDep,
    user_id: PydanticObjectId,
    data: UserRoleUpdateSchema,
):
    user = await user_service.update_user_role(
        user_id=user_id, acting_admin_id=admin, role=data.role
    )

    return success_response(
        data=user,
        message="User role updated successfully",
    )


@admin_routes.delete("/user/{user_id}", description="Delete a user and there content")
async def delete_user(
    user_service: UserServiceDep, user_id: PydanticObjectId, admin: AdminUserDep
):
    await user_service.delete_user(user_id=user_id, acting_admin_id=admin)
    return success_response(message="User deleted successfully")
