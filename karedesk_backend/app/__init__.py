from flask import Flask
from flask_cors import CORS
from .routes.health import blp as health_blp
from .routes.users import blp as users_blp
from .routes.projects import blp as projects_blp
from .routes.support import blp as support_blp
from flask_smorest import Api
from .config import get_config
from .db import create_all_tables  # Import DB helper to optionally create tables

# Initialize Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# API docs configuration
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Load and attach application config (including database config)
_app_cfg = get_config()
# Expose key DB config to Flask config for convenient access in extensions
app.config["DATABASE_URL"] = _app_cfg.database.url
app.config["DB_POOL_SIZE"] = _app_cfg.database.pool_size
app.config["DB_ECHO"] = _app_cfg.database.echo

# Initialize API and register blueprints
api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(users_blp)
api.register_blueprint(projects_blp)
api.register_blueprint(support_blp)

# Ensure DB tables exist if migrations are not configured
try:
    create_all_tables(app)
except Exception as exc:
    # Do not crash app startup in environments without DB; log minimal info.
    # In production, proper logging should be configured.
    print(f"[DB] Skipping automatic create_all due to error: {exc}")
