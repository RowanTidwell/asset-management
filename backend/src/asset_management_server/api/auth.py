"""Authentication helpers used by the API.

This module provides small, well-documented helpers for password hashing,
JWT creation/verification, and FastAPI dependencies used by protected
endpoints.
"""

import os
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from asset_management_server.db import DbSession, models

# Configuration (keep secrets in env vars in production)
SECRET_KEY = os.getenv('JWT_SECRET', 'changeme123')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


# Password hashing/verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage using the configured scheme."""
    return pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
OAuthToken = Annotated[str, Depends(oauth2_scheme)]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT containing `data` and an expiry time.

    `data` should include a `sub` claim (the subject / username) so the
    token can later be resolved back to a user.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(db_sess: Session, username: str):
    """Lookup a `User` by username or return `None` if not found."""
    return db_sess.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db_sess: Session, username: str, password: str):
    """Return user when credentials are valid, else `None`."""
    user = get_user_by_username(db_sess, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: OAuthToken, db_sess: DbSession):
    """FastAPI dependency: decode token and return the corresponding `User`.

    Raises a 401 `HTTPException` when the token is invalid or the user
    cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db_sess, username)
    if user is None:
        raise credentials_exception
    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]

async def get_current_active_user(current_user: CurrentUser):
    """Dependency placeholder: return the user (could enforce `is_active` flag)."""
    return current_user
