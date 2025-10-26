"""Service layer for Reputation operations."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import ReputationRecord, User


def _ensure_user_exists(db: Session, user_id: int) -> None:
    """Validate that a user exists for foreign key constraints."""
    if db.get(User, user_id) is None:
        raise ValueError("User not found")


# PUBLIC_INTERFACE
def list_reputation_records(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
) -> List[ReputationRecord]:
    """Return a paginated list of reputation records with optional filters.

    Args:
        db: SQLAlchemy session.
        limit: Max number of records.
        offset: Number of records to skip.
        user_id: Optional filter by user ID.
        source: Optional filter by source string (company/platform).

    Returns:
        List[ReputationRecord]: Records within requested window.
    """
    stmt = select(ReputationRecord).order_by(ReputationRecord.id)
    if user_id is not None:
        stmt = stmt.filter(ReputationRecord.user_id == int(user_id))
    if source:
        stmt = stmt.filter(ReputationRecord.source == source)

    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


# PUBLIC_INTERFACE
def create_reputation_record(db: Session, data: Dict[str, Any]) -> ReputationRecord:
    """Create a new reputation record.

    Args:
        db: SQLAlchemy session.
        data: Dict with fields: source (str), score (int), notes (str|None), user_id (int)

    Returns:
        ReputationRecord: Created reputation record.

    Raises:
        ValueError: If user does not exist or integrity error occurs.
    """
    user_id = int(data["user_id"])
    _ensure_user_exists(db, user_id)

    record = ReputationRecord(
        source=data["source"],
        score=int(data["score"]),
        notes=data.get("notes"),
        user_id=user_id,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Failed to create reputation record due to integrity constraints") from exc

    db.refresh(record)
    return record


# PUBLIC_INTERFACE
def compute_reputation_summary(
    db: Session,
    user_id: int,
    days: Optional[int] = None,
    source: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute a summary of reputation for a given user, optionally filtered by timeframe and source.

    The summary includes:
    - user_id
    - source (if provided)
    - timeframe_days (if provided)
    - count: number of records
    - total_score: sum of scores
    - avg_score: average score
    - min_score: minimum score
    - max_score: maximum score
    - last_recorded_at: timestamp of most recent record included

    Args:
        db: SQLAlchemy session.
        user_id: Aggregation target user id.
        days: Optional look-back timeframe in days from now.
        source: Optional filter by company/source.

    Returns:
        Dict[str, Any]: Aggregated summary metrics.
    """
    _ensure_user_exists(db, int(user_id))

    stmt = select(
        func.count(ReputationRecord.id),
        func.coalesce(func.sum(ReputationRecord.score), 0),
        func.avg(ReputationRecord.score),
        func.min(ReputationRecord.score),
        func.max(ReputationRecord.score),
        func.max(ReputationRecord.created_at),
    ).filter(ReputationRecord.user_id == int(user_id))

    if source:
        stmt = stmt.filter(ReputationRecord.source == source)

    if days is not None:
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=int(days))
        stmt = stmt.filter(ReputationRecord.created_at >= since)

    count, total, avg, min_s, max_s, last_ts = db.execute(stmt).one()

    # Normalize avg to 0 if None when there are no records
    avg_val: float = float(avg) if avg is not None else 0.0

    result: Dict[str, Any] = {
        "user_id": int(user_id),
        "count": int(count),
        "total_score": int(total),
        "avg_score": avg_val,
        "min_score": int(min_s) if min_s is not None else None,
        "max_score": int(max_s) if max_s is not None else None,
        "last_recorded_at": last_ts.isoformat() if last_ts is not None else None,
    }
    if source:
        result["source"] = source
    if days is not None:
        result["timeframe_days"] = int(days)
    return result
