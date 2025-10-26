import os
from dataclasses import dataclass
from typing import Optional

try:
    # Load environment variables from a .env file if present (dev convenience)
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # If python-dotenv isn't available in some environments, ignore gracefully
    pass


@dataclass(frozen=True)
class DatabaseConfig:
    """Holds database configuration values."""

    url: str
    pool_size: int
    echo: bool


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""
    database: DatabaseConfig


# PUBLIC_INTERFACE
def get_config() -> AppConfig:
    """Return application configuration loaded from environment variables.

    Environment variables:
    - DATABASE_URL: Full database URL (e.g., postgresql+psycopg2://user:pass@host:5432/dbname)
    - DB_POOL_SIZE: SQLAlchemy engine pool size (default: 5)
    - DB_ECHO: Enable SQL echo logging (true/false, default: false)

    Returns:
        AppConfig: Frozen configuration object with database settings.
    """
    db_url = os.getenv(
        "DATABASE_URL",
        # Default to a local Postgres URL format; in production this must be overridden via env.
        "postgresql+psycopg2://postgres:postgres@localhost:5432/karedesk",
    )

    # Pool size: default to 5, ensure integer and minimum of 1
    pool_size_raw: Optional[str] = os.getenv("DB_POOL_SIZE", "5")
    try:
        pool_size = max(1, int(pool_size_raw)) if pool_size_raw is not None else 5
    except ValueError:
        pool_size = 5

    # Echo flag: parse truthy values
    echo_raw = os.getenv("DB_ECHO", "false").strip().lower()
    echo = echo_raw in {"1", "true", "yes", "on"}

    db_cfg = DatabaseConfig(url=db_url, pool_size=pool_size, echo=echo)
    return AppConfig(database=db_cfg)
