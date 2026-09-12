"""Routes for Assets: list, create, and retrieve.

Assets store `metadata` as JSONB which allows pipelines to attach
arbitrary structured data without schema changes.
"""

from typing import Optional
from uuid import UUID

from asset_management_server import crud, schemas
from asset_management_server.api import auth
from asset_management_server.api.routers.utils import fetch_or_404
from asset_management_server.db import DbSession
from fastapi import APIRouter

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("/", response_model=list[schemas.Asset])
def list_assets(
    db: DbSession,
    project_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List assets; optional `project_id` filters assets by project."""
    _project_id = UUID(project_id) if project_id else None
    return crud.get_assets(db, project_id=_project_id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Asset)
def create_asset(
    asset: schemas.AssetCreate,
    db: DbSession,
    current_user: auth.CurrentUser,
):
    """Create a new asset. Authenticated users only."""
    return crud.create_asset(db, asset, creator_id=current_user.id)


@router.get("/{asset_id}", response_model=schemas.Asset)
def get_asset(asset_id: str, db: DbSession):
    """Get asset details by id."""
    return fetch_or_404(crud.get_asset, db, UUID(asset_id))
