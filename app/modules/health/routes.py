from fastapi import APIRouter

health_route = APIRouter()

@health_route.get("/")
def health():
    return 