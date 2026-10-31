from fastapi import APIRouter

from app.modules.health.routes import health_route

app_routes = APIRouter()

app_routes.include_router(health_route)