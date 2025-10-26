"""Marshmallow schemas for Project resource."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class ProjectBaseSchema(Schema):
    """Base schema for Project common fields (no id)."""

    name = fields.String(
        required=True,
        metadata={"description": "Project name"},
        validate=validate.Length(min=1, max=200),
    )
    description = fields.String(
        allow_none=True,
        load_default=None,
        metadata={"description": "Detailed project description"},
    )
    owner_id = fields.Integer(
        required=True,
        metadata={"description": "Owner User ID who created/owns the project"},
    )


class ProjectCreateSchema(ProjectBaseSchema):
    """Schema for creating a project."""
    # Inherits name, description, owner_id


class ProjectUpdateSchema(Schema):
    """Schema for partial updates to a project."""
    name = fields.String(
        required=False,
        metadata={"description": "Project name"},
        validate=validate.Length(min=1, max=200),
    )
    description = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Detailed project description"},
    )
    owner_id = fields.Integer(
        required=False,
        metadata={"description": "Owner User ID who created/owns the project"},
    )


class ProjectSchema(Schema):
    """Schema for reading a project (includes id and timestamps)."""

    id = fields.Integer(dump_only=True, metadata={"description": "Project ID"})
    name = fields.String(required=True, metadata={"description": "Project name"})
    description = fields.String(
        allow_none=True,
        metadata={"description": "Detailed project description"},
    )
    owner_id = fields.Integer(required=True, metadata={"description": "Owner User ID"})
    created_at = fields.DateTime(
        dump_only=True, metadata={"description": "Creation timestamp (UTC)"}
    )
    updated_at = fields.DateTime(
        dump_only=True, metadata={"description": "Last update timestamp (UTC)"}
    )
