"""Small helpers used by routers to reduce repetition.

Functions:
- `fetch_or_404(db_getter, db, id)` - call a crud getter and raise 404 if not found
- `ensure_admin(current_user)` - raise 403 unless user is admin
- `ensure_owner_or_admin(current_user, owner_id)` - raise 403 unless owner or admin
"""

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from asset_management_server import schemas
from fastapi import HTTPException
from sqlalchemy.orm import Session

T_ID = TypeVar("T_ID", str, int, UUID)
T_OBJ = TypeVar("T_OBJ")

def fetch_or_404(getter: Callable[[Session, T_ID], T_OBJ | None], db: Session, id_: T_ID):
    obj = getter(db, id_)
    if not obj:
        raise HTTPException(status_code=404, detail="Resource not found")
    return obj


def ensure_admin(current_user: schemas.User):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin privileges required')


def ensure_owner_or_admin(current_user: schemas.User, owner_id: UUID):
    if current_user.role != 'admin' and current_user.id != owner_id:
        raise HTTPException(status_code=403, detail='Not authorized')
