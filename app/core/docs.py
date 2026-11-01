from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.core.config import settings

# Invert the whole page, then flip back what's already dark or shouldn't change (images, code blocks).
_DARK_CSS = """<style>
html { filter: invert(90%) hue-rotate(180deg); background: #fff; }
img, .microlight, .highlight-code pre { filter: invert(100%) hue-rotate(180deg); }
</style>"""


def docs_kwargs() -> dict[str, Any]:
    """FastAPI() docs options. The schema maps every endpoint and field; don't publish it in production."""
    # if settings.is_production:
    #     return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    # Built-in Swagger page is replaced by the dark one in register_docs().
    return {"docs_url": None}


def register_docs(app: FastAPI) -> None:
    """Serve Swagger UI with a dark theme. No-op in production."""
    # if settings.is_production:
    #     return

    @app.get("/docs", include_in_schema=False)
    async def swagger_ui() -> HTMLResponse:
        page = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{settings.APP_NAME} - Swagger UI",
        )
        return HTMLResponse(
            page.body.decode().replace("</head>", f"{_DARK_CSS}</head>")
        )
