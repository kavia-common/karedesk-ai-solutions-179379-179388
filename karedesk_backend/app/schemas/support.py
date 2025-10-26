"""Marshmallow schemas for Support Ticket resource."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class SupportTicketBaseSchema(Schema):
    """Base schema for SupportTicket common fields (no id)."""

    subject = fields.String(
        required=True,
        metadata={"description": "Ticket subject/title"},
        validate=validate.Length(min=1, max=255),
    )
    message = fields.String(
        required=True,
        metadata={"description": "Detailed message describing the issue"},
        validate=validate.Length(min=1),
    )
    user_id = fields.Integer(
        required=True,
        metadata={"description": "ID del usuario que crea el ticket"},
    )


class SupportTicketCreate(SupportTicketBaseSchema):
    """Schema for creating a support ticket."""
    # Inherits subject, message, user_id


class SupportTicketUpdate(Schema):
    """Schema for partial updates to a support ticket."""
    subject = fields.String(
        required=False,
        metadata={"description": "Ticket subject/title"},
        validate=validate.Length(min=1, max=255),
    )
    message = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Detailed message describing the issue"},
    )
    status = fields.String(
        required=False,
        metadata={"description": "Estado del ticket (open, in_progress, resolved, closed)"},
        validate=validate.OneOf(["open", "in_progress", "resolved", "closed"]),
    )


class SupportTicketRead(Schema):
    """Schema for reading a support ticket (includes id and timestamps)."""

    id = fields.Integer(dump_only=True, metadata={"description": "Ticket ID"})
    subject = fields.String(required=True, metadata={"description": "Ticket subject/title"})
    message = fields.String(required=True, metadata={"description": "Detailed message"})
    status = fields.String(required=True, metadata={"description": "Estado del ticket"})
    user_id = fields.Integer(required=True, metadata={"description": "User ID owner of the ticket"})
    created_at = fields.DateTime(
        dump_only=True, metadata={"description": "Creation timestamp (UTC)"}
    )
    updated_at = fields.DateTime(
        dump_only=True, metadata={"description": "Last update timestamp (UTC)"}
    )
