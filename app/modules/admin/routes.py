from fastapi import APIRouter, Depends

from app.common.pagination import PaginationDep
from app.core.response import build_metadata, success_response
from app.modules.auth.dependencies import require_admin
from app.modules.note.dependencies import NoteServiceDep

admin_routes = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)]
)


@admin_routes.get("/notes")
async def get_all_notes(pageination: PaginationDep, note_service: NoteServiceDep):
    notes, total = await note_service.list_all_notes(
        pageination.skip, pageination.limit
    )
    return success_response(
        data=notes,
        message="All notes fetched successfully",
        metadata=build_metadata(pageination.page, pageination.limit, total),
    )
