"""API routes for managing Projects.

These endpoints are simple wrappers that call into `crud.py` and perform
authorization checks when necessary.
"""

from uuid import UUID

from asset_management_server import crud, schemas
from asset_management_server.api import auth
from asset_management_server.api.routers.utils import ensure_owner_or_admin, fetch_or_404
from asset_management_server.db import DbSession
from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[schemas.Project])
def list_projects(db: DbSession, skip: int = 0, limit: int = 100):
    """List projects with pagination."""
    return crud.get_projects(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: DbSession, current_user: auth.CurrentUser):
    """Create a new project. Authenticated users can create projects."""
    return crud.create_project(db, project, creator_id=current_user.id)


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: str, db: DbSession):
    """Retrieve a single project by id."""
    _project_id = UUID(project_id)
    return fetch_or_404(crud.get_project, db, _project_id)


@router.patch("/{project_id}", response_model=schemas.Project)
def patch_project(project_id: str, project: schemas.ProjectUpdate, db: DbSession, current_user: auth.CurrentUser):
    _project_id = UUID(project_id)
    obj = fetch_or_404(crud.get_project, db, _project_id)
    ensure_owner_or_admin(current_user, obj.created_by)
    return crud.update_project(db, _project_id, project)


@router.delete("/{project_id}")
def delete_project(project_id: str, db: DbSession, current_user: auth.CurrentUser):
    _project_id = UUID(project_id)
    obj = fetch_or_404(crud.get_project, db, _project_id)
    ensure_owner_or_admin(current_user, obj.created_by)
    project_deleted = crud.delete_project(db, _project_id)
    if not project_deleted:
        # unexpected failure
        raise Exception("Failed to delete project")
    return {"status": "deleted"}
