# app/common/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AppError
from app.core.response import error_response


async def app_error_handler(request: Request, exc: AppError):
    return error_response(message=exc.message, status_code=exc.status_code)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(part) for part in err["loc"][1:]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return error_response(
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error=errors,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
