"""
SQLAlchemy session and engine initialization.

This module configures the SQLAlchemy engine and session factory (SessionLocal)
using values from Flask app config (populated from environment variables via app.config).

- DATABASE_URL (str): full DB URL, e.g., postgresql+psycopg2://user:pass@host:5432/db
- DB_POOL_SIZE (int): pool size for SQLAlchemy engine
- DB_ECHO (bool): enable SQL statement echo for debugging

It exposes:
- engine: the SQLAlchemy Engine
- SessionLocal: scoped session factory for request/application usage
- get_db: dependency-style context manager/generator to yield a session

Note: Avoid creating sessions at import time for workers; use get_db or explicit SessionLocal().
"""

from __future__ import annotations

from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Default sane fallbacks; actual values should be injected via Flask config or env variables
DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/karedesk",
)
DEFAULT_POOL_SIZE_RAW = os.getenv("DB_POOL_SIZE", "5")
DEFAULT_DB_ECHO_RAW = os.getenv("DB_ECHO", "false").strip().lower()

try:
    DEFAULT_POOL_SIZE = max(1, int(DEFAULT_POOL_SIZE_RAW))
except Exception:
    DEFAULT_POOL_SIZE = 5

DEFAULT_DB_ECHO = DEFAULT_DB_ECHO_RAW in {"1", "true", "yes", "on"}

# Create SQLAlchemy engine with pool configuration
engine = create_engine(
    DEFAULT_DATABASE_URL,
    pool_size=DEFAULT_POOL_SIZE,
    echo=DEFAULT_DB_ECHO,
    future=True,
)

# Session factory bound to engine
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Any, None, None]:
    """Provide a SQLAlchemy session with proper lifecycle management.

    Usage:
        with contextlib.closing(next(get_db())) as db:
            ...

        or in Flask view:
            for db in get_db():
                ... use db ...
                break

    Yields:
        Session: a SQLAlchemy ORM session bound to the configured engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
