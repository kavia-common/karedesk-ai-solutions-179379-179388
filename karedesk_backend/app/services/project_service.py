"""Service layer for Project operations."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import Project, User


# PUBLIC_INTERFACE
def list_projects(db: Session, limit: int = 100, offset: int = 0) -> List[Project]:
    """Return a paginated list of projects.

    Args:
        db: SQLAlchemy session.
        limit: Maximum number of records to return.
        offset: Number of records to skip.

    Returns:
        List[Project]: Projects within the requested window.
    """
    stmt = select(Project).order_by(Project.id).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


# PUBLIC_INTERFACE
def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Fetch a project by ID.

    Args:
        db: SQLAlchemy session.
        project_id: ID of the project.

    Returns:
        Optional[Project]: The project if found, else None.
    """
    return db.get(Project, project_id)


def _ensure_owner_exists(db: Session, owner_id: int) -> None:
    """Validate that an owner (User) exists."""
    if db.get(User, owner_id) is None:
        raise ValueError("Owner user not found")


# PUBLIC_INTERFACE
def create_project(db: Session, data: Dict[str, Any]) -> Project:
    """Create a new project.

    Args:
        db: SQLAlchemy session.
        data: Dict with fields: name (str), description (str|None), owner_id (int)

    Returns:
        Project: Created project.

    Raises:
        ValueError: If owner does not exist or invalid payload.
    """
    _ensure_owner_exists(db, int(data["owner_id"]))
    project = Project(
        name=data["name"],
        description=data.get("description"),
        owner_id=int(data["owner_id"]),
    )
    db.add(project)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # Possible FK or other integrity issues
        raise ValueError("Failed to create project due to integrity constraints") from exc

    db.refresh(project)
    return project


# PUBLIC_INTERFACE
def update_project(db: Session, project: Project, data: Dict[str, Any]) -> Project:
    """Apply partial updates to a project.

    Args:
        db: SQLAlchemy session.
        project: Existing project instance to modify.
        data: Partial fields to update.

    Returns:
        Project: Updated project.

    Raises:
        ValueError: On integrity violations or invalid data.
    """
    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]
    if "owner_id" in data:
        new_owner_id = int(data["owner_id"])
        _ensure_owner_exists(db, new_owner_id)
        project.owner_id = new_owner_id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Failed to update project due to integrity constraints") from exc

    db.refresh(project)
    return project


# PUBLIC_INTERFACE
def delete_project(db: Session, project: Project) -> None:
    """Delete a project.

    Args:
        db: SQLAlchemy session.
        project: Project instance to delete.
    """
    db.delete(project)
    db.commit()
