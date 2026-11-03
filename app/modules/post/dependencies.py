from typing import Annotated

from fastapi import Depends

from app.modules.post.services import PostService


def get_post_service() -> PostService:
    return PostService()


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
