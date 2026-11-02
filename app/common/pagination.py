from typing import Annotated

from fastapi import Depends, Query

MAX_PAGE = 100_000
MAX_LIMIT = 100


class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1, le=MAX_PAGE),
        limit: int = Query(20, ge=1, le=MAX_LIMIT),
    ):
        self.page = page
        self.limit = limit

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit

PaginationDep = Annotated[Pagination, Depends()]