"""Marshmallow schemas for User resource."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class UserBaseSchema(Schema):
    """Base schema with common user fields (no id)."""

    email = fields.Email(
        required=True,
        metadata={"description": "Unique email address for the user"},
        validate=validate.Length(max=255),
    )
    full_name = fields.String(
        allow_none=True,
        load_default=None,
        metadata={"description": "Full name of the user"},
        validate=validate.Length(max=255),
    )
    role = fields.String(
        required=True,
        load_default="user",
        metadata={"description": "Role of the user"},
        validate=validate.Length(max=50),
    )


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a new user."""
    # Inherit all fields; email and role required by default in base.


class UserUpdateSchema(Schema):
    """Schema for partial updates to a user."""
    email = fields.Email(
        required=False,
        metadata={"description": "Unique email address for the user"},
        validate=validate.Length(max=255),
    )
    full_name = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Full name of the user"},
        validate=validate.Length(max=255),
    )
    role = fields.String(
        required=False,
        metadata={"description": "Role of the user"},
        validate=validate.Length(max=50),
    )


class UserSchema(Schema):
    """Schema for reading a user (includes id and timestamps)."""

    id = fields.Integer(dump_only=True, metadata={"description": "User ID"})
    email = fields.Email(
        required=True,
        metadata={"description": "Unique email address for the user"},
    )
    full_name = fields.String(
        allow_none=True, metadata={"description": "Full name of the user"}
    )
    role = fields.String(required=True, metadata={"description": "Role of the user"})
    created_at = fields.DateTime(
        dump_only=True, metadata={"description": "Creation timestamp (UTC)"}
    )
    updated_at = fields.DateTime(
        dump_only=True, metadata={"description": "Last update timestamp (UTC)"}
    )
