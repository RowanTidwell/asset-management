"""CRUD helpers inside `asset_management_server.api` implementation.

These functions delegate to the database models found in `asset_management_server.models`.
They are intentionally thin so routers can remain small.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from asset_management_server import schemas
from asset_management_server.api.auth import get_password_hash
from asset_management_server.db import models


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: UUID):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, project: schemas.ProjectCreate, creator_id: Optional[UUID] = None):
    db_obj = models.Project(**project.model_dump(), created_by=creator_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_project(db: Session, project_id: UUID, project_update: schemas.ProjectUpdate):
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
    db_obj = get_project(db, project_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True


# Users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, role: str = 'user'):
    hashed = get_password_hash(user.password)
    db_obj = models.User(username=user.username, email=user.email, display_name=user.display_name, hashed_password=hashed, role=role)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
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
    db_obj = get_user(db, user_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True


def change_user_password(db: Session, user_id: UUID, new_password: str):
    db_obj = get_user(db, user_id)
    if not db_obj:
        return None
    db_obj.hashed_password = get_password_hash(new_password)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# Assets / Tasks / etc. can remain in the top-level CRUD module and be
# gradually migrated here as needed.
