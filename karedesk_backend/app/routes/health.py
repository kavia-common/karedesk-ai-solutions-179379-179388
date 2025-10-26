from flask_smorest import Blueprint
from flask.views import MethodView

# Use consistent tag/name for OpenAPI
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")

@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        """Basic health check endpoint.
        Returns:
            dict: A simple JSON message indicating service health.
        """
        return {"message": "Healthy"}
