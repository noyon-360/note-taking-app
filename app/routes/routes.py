from fastapi import APIRouter

from app.modules.admin.routes import admin_routes
from app.modules.auth.routes import auth_routes
from app.modules.health.routes import health_route
from app.modules.note.routes import note_routes
from app.modules.user.routes import user_routes

app_routes = APIRouter()

app_routes.include_router(health_route)
app_routes.include_router(auth_routes)
app_routes.include_router(user_routes)
app_routes.include_router(note_routes)
app_routes.include_router(admin_routes)
