from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = status.HTTP_200_OK,
    metadata: dict | None = None,
):
    body = {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data),
    }
    if metadata is not None:
        body["metadata"] = metadata
    return JSONResponse(content=body, status_code=status_code)


def error_response(
    message: str = "Something went wrong",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error: Any = None,
):
    body = {
        "success": False,
        "message": message,
    }
    if error is not None:
        body["error"] = jsonable_encoder(error)
    return JSONResponse(content=body, status_code=status_code)


def build_metadata(page: int = 1, limit: int = 10, total: int = 0):
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit if limit > 0 else 0,
    }
