from fastapi import status
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import AppError
from app.modules.user.models import User


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

    def update_user(self, user_id, user_data):
        # Logic to update a user's information
        return {"message": f"User {user_id} updated successfully"}

    def delete_user(self, user_id):
        # Logic to delete a user by ID
        return {"message": f"User {user_id} deleted successfully"}
