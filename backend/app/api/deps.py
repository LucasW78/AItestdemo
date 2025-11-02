"""
Dependencies for API endpoints.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db


def get_database() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate if file extension is allowed.
    """
    extension = filename.lower().split('.')[-1]
    return extension in allowed_extensions


def get_current_user():
    """
    Dependency to get current authenticated user.
    Placeholder for future authentication implementation.
    """
    # TODO: Implement authentication
    return {"user_id": "temp_user", "is_authenticated": True}