"""Engine/session factory and DB helpers (moved into `asset_management_server.db`).

This module creates a SQLAlchemy `engine` and `SessionLocal` factory and
exposes two small helpers used by the application and tests:
- `init_db()` — convenience to create tables from `models.Base` (development only)
- `get_db()` — FastAPI dependency that yields a session and closes it.
"""

import os
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from asset_management_server.db.models import Base

# Use the DATABASE_URL environment variable when available.
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./dev.db')

# SQLite requires a `check_same_thread` connect arg when used in a threaded
# context (e.g. tests with TestClient). Determine connect args once to keep
# the engine creation call concise.
is_sqlite = DATABASE_URL.startswith('sqlite')
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory used throughout the app. `autocommit=False` and
# `autoflush=False` keep explicit control of commit/flush behavior.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Create all tables declared on `models.Base`.

    NOTE: prefer Alembic for production schema migrations; this helper is
    convenient for development and tests.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session and ensure it's closed.

    Example usage in a route:

        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]