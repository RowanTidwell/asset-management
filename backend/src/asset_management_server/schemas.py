"""Pydantic schemas for request and response payloads.

This module keeps request (create/update) models separate from response
models. Response models inherit from `OrmModel` which sets `from_attributes=True`
so SQLAlchemy ORM objects can be returned directly from endpoints.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, constr


class OrmModel(BaseModel):
    """Base class for response models that need `from_attributes` enabled.

    Instead of repeating the same `Config` on every response model we
    inherit from `OrmModel` which enables SQLAlchemy object -> Pydantic model
    conversion.
    """

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    role: Optional[str] = 'user'

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: Optional[str]
    new_password: str

class User(UserBase, OrmModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

class ProjectBase(BaseModel):
    name: str
    code: Annotated[str, Field(min_length=1, pattern=r'^[A-Za-z0-9_-]+$')]
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class Project(ProjectBase, OrmModel):
    id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

class Status(OrmModel):
    id: Optional[UUID]
    name: str
    color: Optional[str] = None

class AssetBase(BaseModel):
    name: str
    project_id: UUID
    type: Optional[str] = None
    status_id: Optional[UUID] = None
    metadata: Optional[Any] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase, OrmModel):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

class ShotBase(BaseModel):
    name: str
    project_id: UUID
    sequence: Optional[str] = None
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    status_id: Optional[UUID] = None
    metadata: Optional[Any] = None

class ShotCreate(ShotBase):
    pass

class Shot(ShotBase, OrmModel):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

class TaskBase(BaseModel):
    name: str
    entity_type: str
    entity_id: UUID
    project_id: UUID
    assignee_id: Optional[UUID] = None
    status_id: Optional[UUID] = None
    due_date: Optional[date] = None
    metadata: Optional[Any] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase, OrmModel):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

class CommentCreate(BaseModel):
    entity_type: str
    entity_id: UUID
    body: str
    parent_id: Optional[UUID] = None

class Comment(OrmModel):
    id: UUID
    author_id: Optional[UUID] = None
    entity_type: str
    entity_id: UUID
    body: str
    parent_id: Optional[UUID] = None
    created_at: datetime
