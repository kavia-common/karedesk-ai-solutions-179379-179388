"""Service layer for User operations."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import User


# PUBLIC_INTERFACE
def list_users(db: Session, limit: int = 100, offset: int = 0) -> List[User]:
    """Return a paginated list of users.

    Args:
        db: SQLAlchemy session.
        limit: Maximum number of records to return.
        offset: Number of records to skip.

    Returns:
        List[User]: Users within the requested window.
    """
    stmt = select(User).order_by(User.id).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


# PUBLIC_INTERFACE
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Fetch a user by ID.

    Args:
        db: SQLAlchemy session.
        user_id: ID of the user.

    Returns:
        Optional[User]: The user if found, else None.
    """
    return db.get(User, user_id)


# PUBLIC_INTERFACE
def create_user(db: Session, data: Dict[str, Any]) -> User:
    """Create a new user.

    Args:
        db: SQLAlchemy session.
        data: Dict with fields: email (str), full_name (str|None), role (str)

    Returns:
        User: Created user.

    Raises:
        ValueError: If email is not unique or invalid payload.
    """
    user = User(
        email=data["email"],
        full_name=data.get("full_name"),
        role=data.get("role", "user"),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # Likely unique constraint on email
        raise ValueError("Email already exists") from exc

    db.refresh(user)
    return user


# PUBLIC_INTERFACE
def update_user(db: Session, user: User, data: Dict[str, Any]) -> User:
    """Apply partial updates to a user.

    Args:
        db: SQLAlchemy session.
        user: Existing user instance to modify.
        data: Partial fields to update.

    Returns:
        User: Updated user.

    Raises:
        ValueError: On unique constraint violations or invalid data.
    """
    if "email" in data:
        user.email = data["email"]
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "role" in data:
        user.role = data["role"]

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Email already exists") from exc

    db.refresh(user)
    return user


# PUBLIC_INTERFACE
def delete_user(db: Session, user: User) -> None:
    """Delete a user.

    Args:
        db: SQLAlchemy session.
        user: User instance to delete.
    """
    db.delete(user)
    db.commit()
