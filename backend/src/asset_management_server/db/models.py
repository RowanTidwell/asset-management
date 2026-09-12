from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


# Small mixins to reduce repetition across models and make the intent clear.
class IDMixin:
    """Provides a UUID primary key column named `id`."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )


class TimestampMixin:
    """Provides `created_at` and `updated_at` timestamp columns.

    Using a mixin keeps model classes concise while ensuring all models have
    consistent timestamp behavior.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )


class MetadataMixin:
    """Provides a JSONB `metadata` column stored on the DB as `metadata`.

    The attribute is named `metadata_` to avoid clashing with SQLAlchemy's
    `metadata` module-level symbol. A property could be added if a clean
    `metadata` attribute is preferred at runtime.
    """

    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", 
        JSON,
        default=dict
    )


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column(String, default="user")


class Project(Base, IDMixin, TimestampMixin):
    __tablename__ = "projects"
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="project")
    shots: Mapped[list["Shot"]] = relationship("Shot", back_populates="project")


class Status(Base, IDMixin, TimestampMixin):
    __tablename__ = "statuses"
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String)


class Asset(Base, IDMixin, TimestampMixin, MetadataMixin):
    __tablename__ = "assets"
    name: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE")
    )
    type: Mapped[Optional[str]] = mapped_column(String)
    status_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("statuses.id"))
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    project: Mapped["Optional[Project]"] = relationship("Project", back_populates="assets")


class Shot(Base, IDMixin, TimestampMixin, MetadataMixin):
    __tablename__ = "shots"
    name: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE")
    )
    sequence: Mapped[Optional[str]] = mapped_column(String)
    start_frame: Mapped[int | None] = mapped_column(Integer)
    end_frame: Mapped[int | None] = mapped_column(Integer)
    status_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("statuses.id"))
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    project: Mapped["Optional[Project]"] = relationship("Project", back_populates="shots")


class Task(Base, IDMixin, TimestampMixin, MetadataMixin):
    __tablename__ = "tasks"
    name: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    project_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    assignee_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    status_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("statuses.id"))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))


class Comment(Base, IDMixin, TimestampMixin):
    __tablename__ = "comments"
    author_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("comments.id"))
