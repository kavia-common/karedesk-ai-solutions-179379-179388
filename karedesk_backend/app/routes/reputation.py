"""Reputation API routes with flask-smorest.

Provides operations for digital reputation:
- GET /api/v1/reputation/records: list reputation records with pagination and optional filters (user_id, source)
- POST /api/v1/reputation/records: create a new reputation record
- GET /api/v1/reputation/summary: compute aggregated summary by user and optional timeframe/source
"""

from __future__ import annotations

from flask_smorest import Blueprint
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.reputation import (
    ReputationRecordRead,
    ReputationRecordCreate,
    ReputationSummaryQuery,
)
from app.services.reputation_service import (
    list_reputation_records,
    create_reputation_record,
    compute_reputation_summary,
)

blp = Blueprint(
    "Reputation",
    "reputation",
    url_prefix="/api/v1/reputation",
    description="Operaciones sobre reputación digital",
)


def _get_db() -> Session:
    """Provide a new DB session per request; caller must ensure closure."""
    return SessionLocal()


@blp.route("/records")
class ReputationRecordsCollection(MethodView):
    @blp.response(200, ReputationRecordRead(many=True), description="List reputation records")
    @use_args(
        {
            "limit": fields.Int(missing=100, validate=lambda v: 0 < v <= 200),
            "offset": fields.Int(missing=0, validate=lambda v: v >= 0),
            "user_id": fields.Int(required=False),
            "source": fields.String(required=False),
        },
        location="query",
    )
    def get(self, args):
        """List reputation records with pagination and optional filters.

        Query parameters:
        - limit (int, optional): Max records to return (default 100, max 200).
        - offset (int, optional): Records to skip (default 0).
        - user_id (int, optional): Filter by the owner user id.
        - source (str, optional): Filter by source/company.

        Returns:
            List[ReputationRecord]: Serialized list of reputation records.
        """
        db = _get_db()
        try:
            records = list_reputation_records(
                db,
                limit=args["limit"],
                offset=args["offset"],
                user_id=args.get("user_id"),
                source=args.get("source"),
            )
            return records
        finally:
            db.close()

    @blp.arguments(ReputationRecordCreate)
    @blp.response(201, ReputationRecordRead, description="Created reputation record")
    def post(self, payload):
        """Create a new reputation record.

        Body:
            ReputationRecordCreate: source (required), score (required), notes (optional), user_id (required)

        Returns:
            ReputationRecord: The created reputation record.
        """
        db = _get_db()
        try:
            try:
                record = create_reputation_record(db, payload)
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return record
        finally:
            db.close()


@blp.route("/summary")
class ReputationSummary(MethodView):
    @blp.arguments(ReputationSummaryQuery, location="query")
    def get(self, args):
        """Compute a reputation summary for a given user and optional timeframe/source.

        Query parameters:
        - user_id (int, required): User to compute the summary for.
        - days (int, optional): Look-back timeframe in days.
        - source (str, optional): Filter aggregation by company/source.

        Returns:
            dict: Aggregated metrics including count, total_score, avg_score, min_score, max_score, last_recorded_at, and echo of filters.
        """
        db = _get_db()
        try:
            try:
                result = compute_reputation_summary(
                    db,
                    user_id=int(args["user_id"]),
                    days=args.get("days"),
                    source=args.get("source"),
                )
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return result
        finally:
            db.close()
