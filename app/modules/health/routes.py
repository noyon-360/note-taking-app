from fastapi import APIRouter

from app.core.response import success_response

health_route = APIRouter()


@health_route.get("/")
def health():
    return success_response(message="Health is checking", data={"status": "ok"})
