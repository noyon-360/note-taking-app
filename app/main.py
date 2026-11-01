from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.common.exception_handlers import register_exception_handlers
from app.core.config import settings
from app.core.database import mongodb
from app.core.docs import docs_kwargs, register_docs
from app.routes.routes import app_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    yield
    await mongodb.disconnect()


app = FastAPI(title="Node Taking App", lifespan=lifespan, **docs_kwargs())

register_exception_handlers(app)
register_docs(app)

app.include_router(app_routes, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=settings.PORT)
