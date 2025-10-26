"""Users API routes with flask-smorest.

Provides CRUD operations for users:
- GET /api/v1/users: list users with pagination
- POST /api/v1/users: create a new user
- GET /api/v1/users/<id>: get user by id
- PATCH /api/v1/users/<id>: update user partially
- DELETE /api/v1/users/<id>: delete user
"""

from __future__ import annotations

from flask_smorest import Blueprint
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.users import UserSchema, UserCreateSchema, UserUpdateSchema
from app.services.user_service import (
    list_users,
    create_user,
    get_user as service_get_user,
    update_user as service_update_user,
    delete_user as service_delete_user,
)

blp = Blueprint(
    "Users",
    "users",
    url_prefix="/api/v1/users",
    description="Operations on users",
)


def _get_db() -> Session:
    """Provide a new DB session per request; caller must ensure closure."""
    return SessionLocal()


@blp.route("/")
class UsersCollection(MethodView):
    @blp.response(200, UserSchema(many=True), description="List users")
    @use_args(
        {
            "limit": fields.Int(missing=100, validate=lambda v: 0 < v <= 200),
            "offset": fields.Int(missing=0, validate=lambda v: v >= 0),
        },
        location="query",
    )
    def get(self, args):
        """List users with pagination.

        Query parameters:
        - limit (int, optional): Max records to return (default 100, max 200).
        - offset (int, optional): Records to skip (default 0).

        Returns:
            List[User]: Serialized list of users.
        """
        db = _get_db()
        try:
            users = list_users(db, limit=args["limit"], offset=args["offset"])
            return users
        finally:
            db.close()

    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserSchema, description="Created user")
    def post(self, payload):
        """Create a new user.

        Body:
            UserCreateSchema: email (required), full_name (optional), role (optional, default 'user')

        Returns:
            User: The created user.
        """
        db = _get_db()
        try:
            user = create_user(db, payload)
            return user
        except ValueError as ve:
            blp.abort(409, message=str(ve))
        finally:
            db.close()


@blp.route("/<int:user_id>")
class UserItem(MethodView):
    @blp.response(200, UserSchema, description="User details")
    def get(self, user_id: int):
        """Retrieve a user by ID.

        Path params:
            user_id (int): The user ID.

        Returns:
            User: Serialized user if found, 404 otherwise.
        """
        db = _get_db()
        try:
            user = service_get_user(db, user_id)
            if not user:
                blp.abort(404, message="User not found")
            return user
        finally:
            db.close()

    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema, description="Updated user")
    def patch(self, payload, user_id: int):
        """Partially update a user.

        Path params:
            user_id (int): The user ID.

        Body:
            UserUpdateSchema: Any subset of fields to update.

        Returns:
            User: The updated user.
        """
        db = _get_db()
        try:
            user = service_get_user(db, user_id)
            if not user:
                blp.abort(404, message="User not found")
            try:
                updated = service_update_user(db, user, payload)
            except ValueError as ve:
                blp.abort(409, message=str(ve))
            return updated
        finally:
            db.close()

    @blp.response(204)
    def delete(self, user_id: int):
        """Delete a user by ID.

        Path params:
            user_id (int): The user ID.

        Returns:
            No content on success.
        """
        db = _get_db()
        try:
            user = service_get_user(db, user_id)
            if not user:
                blp.abort(404, message="User not found")
            service_delete_user(db, user)
            return ""
        finally:
            db.close()
