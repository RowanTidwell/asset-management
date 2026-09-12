from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from asset_management_server import crud, db, schemas
from asset_management_server.api import auth
from asset_management_server.api.routers import assets, projects, tasks, users

app = FastAPI(title="Asset Management API")

# Register routers for the resource groups. Each router lives under
# `backend/routers` and keeps endpoint logic organized by domain.
app.include_router(projects.router)
app.include_router(assets.router)
app.include_router(tasks.router)
app.include_router(users.router)


@app.on_event("startup")
def on_startup():
    """Simple startup hook used in development to ensure DB tables exist.

    In production use Alembic migrations; `db.init_db()` is a convenience for
    local development and tests.
    """
    db.init_db()

OAuthRequest = Annotated[OAuth2PasswordRequestForm, Depends()]

@app.post('/auth/token')
def login_for_access_token(form_data: OAuthRequest, db: db.DbSession):
    """Authenticate a user and return a JWT access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/auth/signup')
def signup(user: schemas.UserCreate, db: db.DbSession):
    """Register a new regular user.

    Returns the created user ORM object which is converted to the
    Pydantic response model thanks to `from_attributes`.
    """
    existing = auth.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail='Username already exists')
    created = crud.create_user(db, user, role='user')
    return created


@app.get('/health')
def health():
    return {"status": "ok"}
