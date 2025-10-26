"""
DB package initializer.

Exposes:
- Base: Declarative base for ORM models
- engine, SessionLocal: SQLAlchemy engine and session factory
- create_all_tables(app): Helper to create tables if migrations are not in use

This allows the Flask app to import and, if desired, create tables on startup in
environments where migrations aren't configured.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy import inspect

from .session import engine, SessionLocal
from .models import Base  # Ensure models are imported so metadata is populated


# PUBLIC_INTERFACE
def create_all_tables(flask_app=None) -> None:
    """Create all tables defined in ORM models if they do not already exist.

    Args:
        flask_app: Optional Flask app. If provided, will respect app.config values
                   already applied at process start (engine is created using env/config).
    """
    # Check if database has any of our tables; if none exist, create them.
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if not existing_tables:
        # Create all tables from metadata
        Base.metadata.create_all(bind=engine)
