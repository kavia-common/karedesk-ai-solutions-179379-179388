import os
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .routes.health import blp as health_blp
from .routes.users import blp as users_blp
from .routes.projects import blp as projects_blp
from .routes.support import blp as support_blp
from .routes.reputation import blp as reputation_blp

from .config import get_config
from .db import create_all_tables  # Import DB helper to optionally create tables

# Initialize Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Load configuration from environment via our config helper
_app_cfg = get_config()
# Attach DB config for downstream modules that inspect app.config
app.config["DATABASE_URL"] = _app_cfg.database.url
app.config["DB_POOL_SIZE"] = _app_cfg.database.pool_size
app.config["DB_ECHO"] = _app_cfg.database.echo

# API docs metadata
app.config["API_TITLE"] = os.getenv("API_TITLE", "Karedesk API")
app.config["API_VERSION"] = os.getenv("API_VERSION", "v1")
app.config["OPENAPI_VERSION"] = "3.0.3"
# expose swagger UI under /docs
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# CORS: default allow frontend at http://localhost:3000, overridable by env CORS_ORIGINS
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

# Initialize API and register blueprints
api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(users_blp)
api.register_blueprint(projects_blp)
api.register_blueprint(support_blp)
api.register_blueprint(reputation_blp)

# Try to create tables if migrations aren't being used. Don't fail startup if DB is unreachable.
try:
    create_all_tables(app)
except Exception as exc:
    print(f"[DB] Skipping automatic create_all due to error: {exc}")
