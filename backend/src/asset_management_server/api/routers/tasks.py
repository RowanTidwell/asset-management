 
"""Task endpoints for listing, creating and retrieving tasks."""

from typing import Annotated, Optional
from uuid import UUID

from asset_management_server import crud, schemas
from asset_management_server.api import auth
from asset_management_server.api.routers.utils import fetch_or_404
from asset_management_server.db import DbSession
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[schemas.Task])
def list_tasks(db: DbSession, project_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    """List tasks optionally filtered by project."""
    _project_id = UUID(project_id) if project_id else None
    return crud.get_tasks(db, project_id=_project_id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: DbSession, current_user: auth.CurrentUser):
    """Create a new task assigned to an asset or shot."""
    return crud.create_task(db, task, creator_id=current_user.id)


@router.get("/{task_id}", response_model=schemas.Task)
def get_task(task_id: str, db: DbSession):
    """Retrieve a task by id."""
    return fetch_or_404(crud.get_task, db, UUID(task_id))
