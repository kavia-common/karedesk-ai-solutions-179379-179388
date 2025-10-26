"""Projects API routes with flask-smorest.

Provides CRUD operations for projects:
- GET /api/v1/projects: list projects with pagination
- POST /api/v1/projects: create a new project
- GET /api/v1/projects/<id>: get project by id
- PATCH /api/v1/projects/<id>: update project partially
- DELETE /api/v1/projects/<id>: delete project
"""

from __future__ import annotations

from flask_smorest import Blueprint
from flask.views import MethodView
from webargs import fields
from webargs.flaskparser import use_args
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.projects import (
    ProjectSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
)
from app.services.project_service import (
    list_projects,
    create_project,
    get_project as service_get_project,
    update_project as service_update_project,
    delete_project as service_delete_project,
)

blp = Blueprint(
    "Projects",
    "projects",
    url_prefix="/api/v1/projects",
    description="Operations on projects",
)


def _get_db() -> Session:
    """Provide a new DB session per request; caller must ensure closure."""
    return SessionLocal()


@blp.route("/")
class ProjectsCollection(MethodView):
    @blp.response(200, ProjectSchema(many=True), description="List projects")
    @use_args(
        {
            "limit": fields.Int(missing=100, validate=lambda v: 0 < v <= 200),
            "offset": fields.Int(missing=0, validate=lambda v: v >= 0),
        },
        location="query",
    )
    def get(self, args):
        """List projects with pagination.

        Query parameters:
        - limit (int, optional): Max records to return (default 100, max 200).
        - offset (int, optional): Records to skip (default 0).

        Returns:
            List[Project]: Serialized list of projects.
        """
        db = _get_db()
        try:
            projects = list_projects(db, limit=args["limit"], offset=args["offset"])
            return projects
        finally:
            db.close()

    @blp.arguments(ProjectCreateSchema)
    @blp.response(201, ProjectSchema, description="Created project")
    def post(self, payload):
        """Create a new project.

        Body:
            ProjectCreateSchema: name (required), description (optional), owner_id (required)

        Returns:
            Project: The created project.
        """
        db = _get_db()
        try:
            project = create_project(db, payload)
            return project
        except ValueError as ve:
            blp.abort(400, message=str(ve))
        finally:
            db.close()


@blp.route("/<int:project_id>")
class ProjectItem(MethodView):
    @blp.response(200, ProjectSchema, description="Project details")
    def get(self, project_id: int):
        """Retrieve a project by ID.

        Path params:
            project_id (int): The project ID.

        Returns:
            Project: Serialized project if found, 404 otherwise.
        """
        db = _get_db()
        try:
            project = service_get_project(db, project_id)
            if not project:
                blp.abort(404, message="Project not found")
            return project
        finally:
            db.close()

    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema, description="Updated project")
    def patch(self, payload, project_id: int):
        """Partially update a project.

        Path params:
            project_id (int): The project ID.

        Body:
            ProjectUpdateSchema: Any subset of fields to update.

        Returns:
            Project: The updated project.
        """
        db = _get_db()
        try:
            project = service_get_project(db, project_id)
            if not project:
                blp.abort(404, message="Project not found")
            try:
                updated = service_update_project(db, project, payload)
            except ValueError as ve:
                blp.abort(400, message=str(ve))
            return updated
        finally:
            db.close()

    @blp.response(204)
    def delete(self, project_id: int):
        """Delete a project by ID.

        Path params:
            project_id (int): The project ID.

        Returns:
            No content on success.
        """
        db = _get_db()
        try:
            project = service_get_project(db, project_id)
            if not project:
                blp.abort(404, message="Project not found")
            service_delete_project(db, project)
            return ""
        finally:
            db.close()
