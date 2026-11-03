from beanie import PydanticObjectId
from fastapi import APIRouter, status

from app.common.pagination import PaginationDep
from app.core.response import build_metadata, success_response
from app.modules.auth.dependencies import CurrentUserDep
from app.modules.post.dependencies import PostServiceDep
from app.modules.post.schemas import PostCreateSchema

post_routes = APIRouter(prefix="/posts", tags=["Post"])


@post_routes.post("")
async def create_post(
    post_service: PostServiceDep, data: PostCreateSchema, author: CurrentUserDep
):
    post = await post_service.create_post(author=author, data=data)
    return success_response(
        message="Post created successfully",
        data=post,
        status_code=status.HTTP_201_CREATED,
    )


@post_routes.get("")
async def list_posts(pagination: PaginationDep, post_service: PostServiceDep):
    posts, total = await post_service.list_posts(
        skip=pagination.skip, limit=pagination.limit
    )
    return success_response(
        message="List of post fetch successfully",
        data=posts,
        metadata=build_metadata(
            page=pagination.page, limit=pagination.limit, total=total
        ),
    )


@post_routes.get("{post_id}")
async def get_post(post_id: PydanticObjectId, post_service: PostServiceDep):
    post = await post_service.get_post(post_id=post_id)
    return success_response(message="Post fetch successfully", data=post)
