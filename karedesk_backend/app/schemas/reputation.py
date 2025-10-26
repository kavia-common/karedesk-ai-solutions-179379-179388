"""Marshmallow schemas for Reputation feature (records and summary)."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class ReputationRecordBase(Schema):
    """Base schema for ReputationRecord common fields (no id)."""

    source = fields.String(
        required=True,
        metadata={"description": "Data source of the reputation entry (e.g., google, twitter)"},
        validate=validate.Length(min=1, max=100),
    )
    score = fields.Integer(
        required=True,
        metadata={"description": "Reputation score (arbitrary scale, integer)"},
    )
    notes = fields.String(
        allow_none=True,
        load_default=None,
        metadata={"description": "Optional notes or extra context for the reputation record"},
    )
    user_id = fields.Integer(
        required=True,
        metadata={"description": "User ID that owns this reputation record"},
    )


class ReputationRecordCreate(ReputationRecordBase):
    """Schema for creating a reputation record."""
    # Inherits source, score, notes, user_id


class ReputationRecordRead(Schema):
    """Schema for reading a reputation record (includes id and timestamps)."""

    id = fields.Integer(dump_only=True, metadata={"description": "ReputationRecord ID"})
    source = fields.String(required=True, metadata={"description": "Data source of the reputation entry"})
    score = fields.Integer(required=True, metadata={"description": "Reputation score"})
    notes = fields.String(allow_none=True, metadata={"description": "Optional notes"})
    user_id = fields.Integer(required=True, metadata={"description": "Owner User ID"})
    created_at = fields.DateTime(
        dump_only=True, metadata={"description": "Creation timestamp (UTC)"}
    )
    updated_at = fields.DateTime(
        dump_only=True, metadata={"description": "Last update timestamp (UTC)"}
    )


class ReputationSummaryQuery(Schema):
    """Schema for the query parameters to compute a reputation summary."""

    user_id = fields.Integer(
        required=True,
        metadata={"description": "User ID to aggregate reputation for"},
    )
    # Timeframe in days to look back from now. If omitted, use all-time.
    days = fields.Integer(
        required=False,
        allow_none=True,
        metadata={"description": "Optional number of days to include in the summary (look-back)."},
        validate=validate.Range(min=1),
    )
    # Optional filter by source/company (e.g., 'google', 'twitter')
    source = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Optional source/company filter (e.g., google, twitter)"},
        validate=validate.Length(min=1, max=100),
    )
