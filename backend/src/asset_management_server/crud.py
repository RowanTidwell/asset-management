"""
CRUD helpers for the application.

This module exposes functions that operate against a SQLAlchemy `Session`.
Each helper accepts a `db` session and ORM / Pydantic objects. The comments
below explain common patterns used across the functions so developers who are
new to relational databases and SQLAlchemy can follow the intent.

Key concepts used in this file:
- `Session` (SQLAlchemy): represents a DB transaction/context. You `add()`
    objects to the session, then `commit()` to persist them. Use `refresh()` to
    re-load fields set by the database (e.g., default timestamps, generated IDs).
- `commit()` finalizes the transaction. If multiple operations must succeed
    together, they should be executed within a single session/transaction.
- `refresh(obj)` reloads the ORM object from the DB so it contains any DB-side
    defaults or triggers applied during the insert/update.
- `exclude_unset=True` on Pydantic `.dict()` is used to support PATCH-style
    partial updates (only fields provided by the client are applied).
"""

import uuid
from typing import Optional

from asset_management_server.api.crud import *  # re-export CRUD from `asset_management_server.api.crud`


def get_project(db: Session, project_id: UUID):
        """Return a single project by id or None.

        - We accept either a UUID instance or a string representation. Converting
            strings to `uuid.UUID` ensures the value matches the typed UUID column
            used by SQLAlchemy.
        - `.first()` executes the query and returns the first matching ORM object
            or `None` if no row matched.
        """
        if isinstance(project_id, str):
                # Coerce string IDs to UUID objects so SQLAlchemy's typed UUID columns
                # receive the correct Python type. This avoids confusing errors like
                # "'str' has no attribute 'hex'" when the ORM expects a UUID.
                project_id = uuid.UUID(project_id)
        return db.query(models.Project).filter(models.Project.id == project_id).first()

def create_project(db: Session, project: schemas.ProjectCreate, creator_id: Optional[UUID] = None):
    """Insert a new project and return the created ORM object.

    Typical insertion pattern:
    1. Build an ORM object using fields from a Pydantic model (`.dict()`).
    2. `add()` it to the session so SQLAlchemy tracks it.
    3. `commit()` to persist changes to the database.
    4. `refresh()` the object to populate any DB-generated fields (IDs,
       timestamps, default statuses).
    """
    db_obj = models.Project(**project.model_dump(), created_by=creator_id)
    db.add(db_obj)
    db.commit()
    # refresh causes SQLAlchemy to re-query the DB for this object's state,
    # filling fields like `id` or server-side default columns.
    db.refresh(db_obj)
    return db_obj

def update_project(db: Session, project_id: UUID, project_update: schemas.ProjectUpdate):
    """Apply partial updates from a `ProjectUpdate` and return the object.

    PATCH semantics:
    - We use `exclude_unset=True` so only fields provided by the client are
      changed. This allows clients to send a small payload containing only the
      fields they want to update.
    - `setattr()` updates the in-memory ORM object. A subsequent `commit()`
      flushes changes to the DB.
    """
    db_obj = get_project(db, project_id)
    if not db_obj:
        return None
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_project(db: Session, project_id: UUID):
        """Delete a project. Returns True on success, False if not found.

        Deletion notes:
        - `db.delete(obj)` marks the ORM instance for deletion; `commit()` executes
            the DELETE in the database.
        - Be mindful of foreign key constraints: deleting a parent row may fail if
            child rows still reference it. The higher-level API should enforce
            business rules (e.g., disallow deletion when children exist).
        """
        db_obj = get_project(db, project_id)
        if not db_obj:
                return False
        db.delete(db_obj)
        db.commit()
        return True

# Users
def get_users(db: Session, skip: int = 0, limit: int = 100):
        """List users with simple pagination. Admin-only in the API layer.

        Pagination basics:
        - `offset(skip).limit(limit)` implements simple page semantics. For large
            datasets consider cursor-based pagination for efficiency and stability.
        """
        return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: UUID):
    """Return a user by id or None.

    We coerce string IDs to `uuid.UUID` similar to other getters to ensure the
    query matches the typed UUID column.
    """
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate, role: str = 'user'):
        """Create a new user with a hashed password. Returns the ORM object.

        Security notes:
        - Passwords must never be stored in plaintext. `get_password_hash()` uses a
            secure hashing algorithm (bcrypt in production). Tests may override the
            hashing scheme for portability.
        - The hashing function should include a salt and be intentionally slow to
            resist brute-force attacks.
        """
        hashed = get_password_hash(user.password)
        db_obj = models.User(username=user.username, email=user.email, display_name=user.display_name, hashed_password=hashed, role=role)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
    """Apply partial updates to a user and return the ORM object.

    Be careful when updating sensitive fields (like `role` or `hashed_password`)
    — make sure the calling endpoint enforces proper authorization and
    validation.
    """
    db_obj = get_user(db, user_id)
    if not db_obj:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_user(db: Session, user_id: UUID):
    """Delete a user by id. Returns True if deleted.

    Consider instead marking accounts as disabled or archived if you need to
    retain history or references to the user (soft delete pattern).
    """
    db_obj = get_user(db, user_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True

def change_user_password(db: Session, user_id: UUID, new_password: str):
    """Set a new password for a user (hashes before storing).

    This replaces the stored hash with a hash of the new password. Ensure the
    calling code verifies the requestor is authorized to change the password.
    """
    db_obj = get_user(db, user_id)
    if not db_obj:
        return None
    db_obj.hashed_password = get_password_hash(new_password)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Assets
def get_assets(db: Session, project_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
    # Start a query against the Asset table. We optionally filter by
    # `project_id` to return only assets belonging to a specific project.
    q = db.query(models.Asset)
    if project_id:
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        q = q.filter(models.Asset.project_id == project_id)
    return q.offset(skip).limit(limit).all()

def get_asset(db: Session, asset_id: UUID):
    # Fetch a single asset by its primary key. `.first()` returns None when no
    # row matches, which is convenient for endpoint logic that then returns
    # 404 Not Found to the client.
    return db.query(models.Asset).filter(models.Asset.id == asset_id).first()

def create_asset(db: Session, asset: schemas.AssetCreate, creator_id: Optional[UUID] = None):
    db_obj = models.Asset(**asset.model_dump(), created_by=creator_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Tasks
def get_tasks(db: Session, project_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
    q = db.query(models.Task)
    if project_id:
        q = q.filter(models.Task.project_id == project_id)
    return q.offset(skip).limit(limit).all()

def get_task(db: Session, task_id: UUID):
    if isinstance(task_id, str):
        task_id = uuid.UUID(task_id)
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate, creator_id: Optional[UUID] = None):
    db_obj = models.Task(**task.model_dump(), created_by=creator_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
