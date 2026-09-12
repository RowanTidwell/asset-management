import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from passlib.context import CryptContext

# Configure the testing engine/session BEFORE importing app so
# FastAPI dependencies and startup use the testing DB.
DATABASE_URL = "sqlite:///:memory:"
# Use StaticPool so the same in-memory database is reused across threads/connections
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import importlib

import asset_management_server.db as _dbpkg

_db_mod = importlib.import_module("asset_management_server.db.db")

# Ensure both the package-level and the internal `asset_management_server.db` module
# use the testing engine/session so `db.init_db()` operates on the
# in-memory DB during test startup.
_dbpkg.engine = engine
_dbpkg.SessionLocal = TestingSessionLocal
_db_mod.engine = engine
_db_mod.SessionLocal = TestingSessionLocal

# Import models/auth after engine is configured so model metadata
# and any DB helpers bind to the testing engine.
import importlib

from asset_management_server.db import models

api_auth = importlib.import_module('asset_management_server.api.auth')

# Note: we create/drop tables per-test in the `client` fixture to ensure a
# clean database state for each test. This keeps tests isolated and avoids
# cross-test leakage when the suite is run in different orders.

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use a test-friendly password hashing scheme to avoid bcrypt platform
# issues and the 72-byte bcrypt limit during tests.
# Ensure the API auth module uses the test-friendly hashing scheme so
# password verification in the app endpoints matches how we hash test users.
api_auth.pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
# Also update the top-level shim module if it was imported elsewhere.
try:
    from asset_management_server.api import auth as top_auth
    top_auth.pwd_context = api_auth.pwd_context
except Exception:
    pass

# Now import the FastAPI app and apply dependency overrides
from asset_management_server.db import get_db
from asset_management_server.main import app

app.dependency_overrides[get_db] = override_get_db
# Also override any internal module get_db references so route dependencies
# resolve to the testing session regardless of which symbol was imported.
try:
    app.dependency_overrides[_db_mod.get_db] = override_get_db
except Exception:
    pass


@pytest.fixture(scope='function')
def client():
    # Ensure admin user exists before starting TestClient so the
    # app's request-handling thread can see the committed record.
    # Recreate the schema to guarantee a fresh DB for this test
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    admin = models.User(
        username='admin',
        email='admin@example.com',
        display_name='Admin',
        hashed_password=api_auth.get_password_hash('secret'),
        role='admin'
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()

    # Use a TestClient context so startup/shutdown events run for each test
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='function')
def admin_token(client):
    # Ensure admin user exists in the testing DB using the test hashing scheme.
    # Request a token from the running app (admin user already created).
    resp = client.post('/auth/token', data={'username': 'admin', 'password': 'secret'})
    assert resp.status_code == 200, resp.text
    return resp.json()['access_token']
