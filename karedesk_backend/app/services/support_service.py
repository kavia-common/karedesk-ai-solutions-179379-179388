"""Service layer for Support Ticket operations."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import SupportTicket, User


VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}


def _ensure_user_exists(db: Session, user_id: int) -> None:
    """Validate that a user exists for foreign key constraints."""
    if db.get(User, user_id) is None:
        raise ValueError("User not found")


# PUBLIC_INTERFACE
def list_support_tickets(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> List[SupportTicket]:
    """Return a paginated list of support tickets with optional filters.

    Args:
        db: SQLAlchemy session.
        limit: Max number of records.
        offset: Number of records to skip.
        status: Optional filter by status.
        user_id: Optional filter by user ID.

    Returns:
        List[SupportTicket]: Tickets within requested window.
    """
    stmt = select(SupportTicket).order_by(SupportTicket.id)

    if status:
        if status not in VALID_STATUSES:
            raise ValueError("Invalid status filter")
        stmt = stmt.filter(SupportTicket.status == status)
    if user_id is not None:
        stmt = stmt.filter(SupportTicket.user_id == int(user_id))

    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


# PUBLIC_INTERFACE
def get_support_ticket(db: Session, ticket_id: int) -> Optional[SupportTicket]:
    """Fetch a support ticket by ID.

    Args:
        db: SQLAlchemy session.
        ticket_id: ID of the support ticket.

    Returns:
        Optional[SupportTicket]: The ticket if found, else None.
    """
    return db.get(SupportTicket, ticket_id)


# PUBLIC_INTERFACE
def create_support_ticket(db: Session, data: Dict[str, Any]) -> SupportTicket:
    """Create a new support ticket.

    Args:
        db: SQLAlchemy session.
        data: Dict with fields: subject (str), message (str), user_id (int)

    Returns:
        SupportTicket: Created support ticket.

    Raises:
        ValueError: If user does not exist or invalid payload.
    """
    user_id = int(data["user_id"])
    _ensure_user_exists(db, user_id)

    ticket = SupportTicket(
        subject=data["subject"],
        message=data["message"],
        user_id=user_id,
        # status defaults to "open" in the model
    )
    db.add(ticket)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Failed to create ticket due to integrity constraints") from exc

    db.refresh(ticket)
    return ticket


# PUBLIC_INTERFACE
def update_support_ticket(db: Session, ticket: SupportTicket, data: Dict[str, Any]) -> SupportTicket:
    """Apply partial updates to a support ticket.

    Args:
        db: SQLAlchemy session.
        ticket: Existing ticket instance to modify.
        data: Partial fields to update.

    Returns:
        SupportTicket: Updated ticket.

    Raises:
        ValueError: On invalid data or integrity issues.
    """
    if "subject" in data:
        ticket.subject = data["subject"]
    if "message" in data:
        ticket.message = data["message"]
    if "status" in data:
        new_status = data["status"]
        if new_status not in VALID_STATUSES:
            raise ValueError("Invalid status value")
        ticket.status = new_status

    if "user_id" in data:
        # Allow reassignment if needed, but ensure user exists
        new_user_id = int(data["user_id"])
        _ensure_user_exists(db, new_user_id)
        ticket.user_id = new_user_id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Failed to update ticket due to integrity constraints") from exc

    db.refresh(ticket)
    return ticket
