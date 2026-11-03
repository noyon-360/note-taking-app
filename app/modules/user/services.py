from beanie import PydanticObjectId, UpdateResponse
from beanie.operators import Set
from fastapi import status
from pymongo.errors import DuplicateKeyError

from app.common.enum import UserRole
from app.core.exceptions import AppError
from app.modules.note.models import Note
from app.modules.user.models import User
from app.modules.user.pipelines import interest_group_pipeline, user_post_pipeline
from app.modules.user.schemas import UserResponse, UserUpdateSchema


class UserService:
    async def create_user(
        self, *, name: str, email: str, pass_hash: str, role: str, interests: list[str]
    ) -> User:
        user = User(
            name=name, email=email, pass_hash=pass_hash, role=role, interests=interests
        )
        try:
            await user.insert()
        except DuplicateKeyError:
            raise AppError("Email already registered", status.HTTP_409_CONFLICT)
        return user

    async def get_user_by_email(self, email: str) -> User:
        # Logic to retrieve a user by email
        return await User.find_one(User.email == email)

    async def list_users(self, skip: int, limit: int) -> tuple[list[UserResponse], int]:
        users = await User.find_all().sort("_id").skip(skip).limit(limit).to_list()
        total = await User.get_pymongo_collection().estimated_document_count()
        return [UserResponse.model_validate(user) for user in users], total

    async def get_user_by_id(self, user_id: PydanticObjectId) -> UserResponse:
        user = await User.get(user_id)
        if user is None:
            raise AppError("User not found", status.HTTP_404_NOT_FOUND)
        return UserResponse.model_validate(user)

    async def update_user(
        self, user_id: PydanticObjectId, user_data: UserUpdateSchema
    ) -> UserResponse:
        fields = user_data.model_dump(exclude_none=True)

        if not fields:
            return await self.get_user_by_id(user_id=user_id)

        try:
            user = await User.find_one(User.id == user_id).update(
                Set(fields), response_type=UpdateResponse.NEW_DOCUMENT
            )
        except DuplicateKeyError:
            raise AppError(
                "Email already registered", status_code=status.HTTP_409_CONFLICT
            )

        if user is None:
            raise AppError("User not found", status_code=status.HTTP_404_NOT_FOUND)
        return UserResponse.model_validate(user)

    async def update_user_role(
        self,
        user_id: PydanticObjectId,
        acting_admin_id: PydanticObjectId,
        role: UserRole,
    ) -> UserResponse:
        if user_id == acting_admin_id:
            raise AppError(
                message="You can't change your own role",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        user = await User.find_one(User.id == user_id).update(
            Set({User.role: role}), response_type=UpdateResponse.NEW_DOCUMENT
        )
        if user is None:
            raise AppError(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return UserResponse.model_validate(user)

    async def delete_user(
        self,
        user_id: PydanticObjectId,
        acting_admin_id: PydanticObjectId,
    ):
        if user_id == acting_admin_id:
            raise AppError(
                "You can't delete yourself", status_code=status.HTTP_403_FORBIDDEN
            )
        await self._delete_user_by_content(user_id=user_id)

    async def delete_own_account(self, user: User) -> None:
        if user.role == UserRole.ADMIN:
            raise AppError(
                message="Admins can't delete their own account",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        await self._delete_user_by_content(user_id=user.id)

    async def _delete_user_by_content(self, user_id: PydanticObjectId) -> None:
        user = await User.get(user_id)
        if user is None:
            raise AppError(
                message="User Not found", status_code=status.HTTP_404_NOT_FOUND
            )

        await Note.find(Note.owner_id == user_id).delete()
        await user.delete()

    async def get_interest_groups(
        self, interests: list[str] | None, skip: int, limit: int, users_per_group: int
    ) -> tuple[list[dict], int]:
        normalized = [interest.strip().lower() for interest in interests or []]
        pipeline = interest_group_pipeline(
            interests=normalized,
            skip=skip,
            limit=limit,
            users_per_group=users_per_group,
        )

        result = await User.aggregate(pipeline, allowDiskUse=True).to_list()

        facet = result[0]
        total = facet["metadata"][0]["total"] if facet["metadata"] else 0
        return facet["data"], total

    async def get_user_posts(
        self, user_id: PydanticObjectId, skip: int, limit: int
    ) -> dict:
        pipeline = user_post_pipeline(user_id=user_id, skip=skip, limit=limit)

        result = await User.aggregate(pipeline).to_list()

        if not result:
            raise AppError(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return result[0]
