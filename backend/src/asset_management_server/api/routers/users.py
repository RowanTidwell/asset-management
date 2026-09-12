
"""User management routes including signup, self-service and admin operations.

Endpoints:
- `POST /users/` - create user (admin-only)
- `GET /users/` - list users (admin-only)
- `GET /users/me` - get current user
- `GET /users/{id}` - get user (admin or self)
- `PATCH /users/{id}` - update user (admin or self)
- `POST /users/{id}/change-password` - change password
- `DELETE /users/{id}` - delete user (admin or self)
"""

from uuid import UUID

from asset_management_server import crud, schemas
from asset_management_server.api import auth
from asset_management_server.api.routers.utils import ensure_admin, fetch_or_404
from asset_management_server.db import DbSession
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])

@router.post('/', response_model=schemas.User)
def create_user_admin(user: schemas.UserCreate, db: DbSession, current_user: auth.CurrentUser):
    """Create a user (admin-only)."""
    ensure_admin(current_user)
    user_role = 'user'
    if hasattr(user, 'role'):
        user_role = user.role or user_role
    return crud.create_user(db, user, role=user_role)


@router.get('/', response_model=list[schemas.User])
def list_users(
    db: DbSession,
    current_user: auth.CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    """List users (admin-only)."""
    ensure_admin(current_user)
    return crud.get_users(db, skip=skip, limit=limit)


@router.get('/me', response_model=schemas.User)
def read_me(current_user: auth.CurrentUser):
    """Return the authenticated user's profile."""
    return current_user


@router.get('/{user_id}', response_model=schemas.User)
def get_user(user_id: str, db: DbSession, current_user: auth.CurrentUser):
    """Get a user by id. Admins can fetch any user; users can fetch themselves."""
    obj = fetch_or_404(crud.get_user, db, UUID(user_id))
    if current_user.role != 'admin' and current_user.id != obj.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return obj


@router.patch('/{user_id}', response_model=schemas.User)
def patch_user(user_id: str, user: schemas.UserUpdate, db: DbSession, current_user: auth.CurrentUser):
    """Update user fields. Only admins may change the `role` field."""
    obj = fetch_or_404(crud.get_user, db, UUID(user_id))
    # only admin can change role
    if 'role' in (user.model_dump(exclude_unset=True)) and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can change roles')
    if current_user.role != 'admin' and current_user.id != obj.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    return crud.update_user(db, UUID(user_id), user)


@router.post('/{user_id}/change-password')
def change_password(user_id: str, pw: schemas.PasswordChange, db: DbSession, current_user: auth.CurrentUser):
    """Change a user's password.

    Admins may change any user's password without the old password. Regular
    users must supply their current password in `old_password`.
    """
    obj = fetch_or_404(crud.get_user, db, UUID(user_id))
    # allow admin to change without old password
    if current_user.role != 'admin' and current_user.id != obj.id:
        raise HTTPException(status_code=403, detail='Not authorized')
    if current_user.role != 'admin' and not auth.verify_password(pw.old_password, obj.hashed_password):
        # verify old password
        raise HTTPException(status_code=400, detail='Old password incorrect')
    crud.change_user_password(db, UUID(user_id), pw.new_password)
    return {'status': 'password_changed'}


@router.delete('/{user_id}')
def delete_user(user_id: str, db: DbSession, current_user: auth.CurrentUser):
    """Delete a user (admin or self)."""
    if current_user.role != 'admin' and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail='Not authorized')
    ok = crud.delete_user(db, UUID(user_id))
    if not ok:
        raise HTTPException(status_code=404, detail='User not found')
    return {'status': 'deleted'}
