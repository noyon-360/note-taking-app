from beanie import PydanticObjectId
from fastapi import status

from app.core.exceptions import AppError
from app.modules.post.models import Post
from app.modules.post.schemas import PostCreateSchema, PostResponse
from app.modules.user.models import User


class PostService:
    async def create_post(self, author: User, data: PostCreateSchema) -> PostResponse:
        post = Post(title=data.title, content=data.content, author_id=author.id)
        await post.insert()

        return PostResponse.model_validate(post)

    async def list_posts(self, skip: int, limit: int) -> tuple[list[PostResponse], int]:
        posts = await Post.find_all().sort("-_id").skip(skip).limit(limit).to_list()
        total = await Post.get_pymongo_collection().estimated_document_count()

        return [PostResponse.model_validate(post) for post in posts], total

    async def get_post(self, post_id: PydanticObjectId) -> PostResponse:
        post = await Post.get(post_id)
        if post is None:
            raise AppError(
                message="Post not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return PostResponse.model_validate(post)
