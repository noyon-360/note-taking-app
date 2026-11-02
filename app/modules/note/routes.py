from fastapi import APIRouter, status

from app.common.pagination import PaginationDep
from app.core.response import build_metadata, success_response
from app.modules.auth.dependencies import CurrentUserDep
from app.modules.note.dependencies import NoteServiceDep
from app.modules.note.schemas import NoteCreateSchema

note_routes = APIRouter(prefix="/notes", tags=["Notes"])


@note_routes.post("", status_code=status.HTTP_201_CREATED)
async def create_note(
    data: NoteCreateSchema, current_user: CurrentUserDep, note_service: NoteServiceDep
):
    note = await note_service.create_note(current_user, data)
    return success_response(
        data=note,
        message="Note created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@note_routes.get("")
async def get_notes(
    pageination: PaginationDep,
    current_user: CurrentUserDep,
    note_service: NoteServiceDep,
):
    notes, total = await note_service.list_notes_for_owner(
        current_user.id, pageination.skip, pageination.limit
    )
    return success_response(
        data=notes,
        message="Notes fetched successfully",
        metadata=build_metadata(pageination.page, pageination.limit, total),
    )


@note_routes.get("/{note_id}")
async def get_note(note_id: str):
    return {"message": f"Details of note {note_id}"}


@note_routes.patch("/{note_id}")
async def update_note(note_id: str):
    return {"message": f"Note {note_id} updated successfully"}


@note_routes.delete("/{note_id}")
async def delete_note(note_id: str):
    return {"message": f"Note {note_id} deleted successfully"}
