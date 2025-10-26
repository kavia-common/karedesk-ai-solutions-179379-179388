"""Support Tickets API routes with flask-smorest.

Provides operations for support tickets:
- GET /api/v1/support/tickets: list tickets with pagination and optional filters (status, user_id)
- POST /api/v1/support/tickets: create a new ticket
- GET /api/v1/support/tickets/<id>: get ticket by id
- PATCH /api/v1/support/tickets/<id>: update ticket partially (subject, message, status, user_id)
"""

from __future__ import annotations

from flask_smorest import Blueprint
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.support import (
    SupportTicketRead,
    SupportTicketCreate,
    SupportTicketUpdate,
)
from app.services.support_service import (
    list_support_tickets,
    create_support_ticket,
    get_support_ticket as service_get_ticket,
    update_support_ticket as service_update_ticket,
)

blp = Blueprint(
    "Support",
    "support",
    url_prefix="/api/v1/support/tickets",
    description="Operaciones sobre tickets de soporte",
)


def _get_db() -> Session:
    """Provide a new DB session per request; caller must ensure closure."""
    return SessionLocal()


@blp.route("/")
class SupportTicketsCollection(MethodView):
    @blp.response(200, SupportTicketRead(many=True), description="List support tickets")
    @use_args(
        {
            "limit": fields.Int(missing=100, validate=lambda v: 0 < v <= 200),
            "offset": fields.Int(missing=0, validate=lambda v: v >= 0),
            "status": fields.String(required=False),
            "user_id": fields.Int(required=False),
        },
        location="query",
    )
    def get(self, args):
        """List support tickets with pagination and optional filters.

        Query parameters:
        - limit (int, optional): Max records to return (default 100, max 200).
        - offset (int, optional): Records to skip (default 0).
        - status (str, optional): Filter by status (open, in_progress, resolved, closed).
        - user_id (int, optional): Filter by the ticket owner user id.

        Returns:
            List[SupportTicket]: Serialized list of tickets.
        """
        db = _get_db()
        try:
            try:
                tickets = list_support_tickets(
                    db,
                    limit=args["limit"],
                    offset=args["offset"],
                    status=args.get("status"),
                    user_id=args.get("user_id"),
                )
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return tickets
        finally:
            db.close()

    @blp.arguments(SupportTicketCreate)
    @blp.response(201, SupportTicketRead, description="Created support ticket")
    def post(self, payload):
        """Create a new support ticket.

        Body:
            SupportTicketCreate: subject (required), message (required), user_id (required)

        Returns:
            SupportTicket: The created ticket.
        """
        db = _get_db()
        try:
            try:
                ticket = create_support_ticket(db, payload)
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return ticket
        finally:
            db.close()


@blp.route("/<int:ticket_id>")
class SupportTicketItem(MethodView):
    @blp.response(200, SupportTicketRead, description="Support ticket details")
    def get(self, ticket_id: int):
        """Retrieve a support ticket by ID.

        Path params:
            ticket_id (int): The ticket ID.

        Returns:
            SupportTicket: Serialized ticket if found, 404 otherwise.
        """
        db = _get_db()
        try:
            ticket = service_get_ticket(db, ticket_id)
            if not ticket:
                blp.abort(404, message="Support ticket not found")
            return ticket
        finally:
            db.close()

    @blp.arguments(SupportTicketUpdate)
    @blp.response(200, SupportTicketRead, description="Updated support ticket")
    def patch(self, payload, ticket_id: int):
        """Partially update a support ticket.

        Path params:
            ticket_id (int): The ticket ID.

        Body:
            SupportTicketUpdate: Any subset of fields to update (subject, message, status, user_id).

        Returns:
            SupportTicket: The updated ticket.
        """
        db = _get_db()
        try:
            ticket = service_get_ticket(db, ticket_id)
            if not ticket:
                blp.abort(404, message="Support ticket not found")
            try:
                updated = service_update_ticket(db, ticket, payload)
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return updated
        finally:
            db.close()
