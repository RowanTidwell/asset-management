# COMPONENTS: mapping of backend code to logical areas

This file explains which files currently belong to which component (API, CLI, Database, Infrastructure, Tests, Scripts), and proposes a safe reorganization plan so the codebase better communicates responsibilities.

Current layout (backend/)

- API
    - `main.py` - FastAPI app entrypoint and router registration
    - `auth.py` - authentication helpers and FastAPI dependencies
    - `schemas.py` - Pydantic request/response schemas
    - `crud.py` - higher-level DB helpers used by routes
    - `routers/` - FastAPI route modules (projects, users, assets, tasks, etc.)

- Database
    - `models.py` - SQLAlchemy ORM models
    - `db.py` - engine/session factory and `get_db` dependency
    - `alembic/`, `alembic.ini` - migrations
    - `requirements-lock.txt`, `requirements.txt` (deps used by DB & API)

- Infrastructure & packaging
    - `Dockerfile` - container build for production
    - `scripts/` - helper scripts (generate-lock.sh)

- Testing
    - `tests/` - pytest tests for backend
    - `pytest.ini` - pytest config

- Virtualenv
    - `.venv/` - local virtualenv (should be gitignored)

Goals for a clearer repository structure

1. Make it obvious where to find API vs DB vs CLI code.
2. Avoid breaking imports immediately — propose a staged reorg with compatibility shims.
3. Provide a small `cli/` package (even if lightweight) so future CLI code has a clear home.

Recommended reorganization (safe staged approach)

Stage A — documentation + component markers (non-breaking)

- Add this `COMPONENTS.md` (done).
- Create `api/`, `db/`, `cli/`, `infra/`, `tests/` folders and add lightweight `__init__.py` or index modules that import the existing modules. Example:
    - `api/__init__.py` could import from the top-level `backend` package: `from asset_management_server import main as app_main`

Stage B — move files and add compatibility shims

- Physically move files to the new folders:
    - `models.py`, `db.py`, `alembic/` -> `db/`
- Add small shim modules at the old locations that re-export names for backward compatibility. Example `asset_management_server/main.py` becomes a shim that imports and exposes `api.main` objects so imports elsewhere still work while code is updated.

Stage C — update imports and cleanup

- Adjust all internal imports to the new layout (e.g., `from asset_management_server.db import get_db` -> `from asset_management_server.db.db import get_db` or `from asset_management_server.db import get_db` if you expose in `db/__init__.py`).
- Remove shim modules once callers are updated.
