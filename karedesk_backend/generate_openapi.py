import json
import os

# Importing app will register all blueprints and construct the Api/spec
from app import app, api  # noqa: E402

def main() -> None:
    """Generate OpenAPI spec from the running Flask-Smorest Api and write it to interfaces/openapi.json."""
    with app.app_context():
        spec_dict = api.spec.to_dict()

    output_dir = os.path.join(os.path.dirname(__file__), "interfaces")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec_dict, f, indent=2)
    print(f"OpenAPI spec written to {output_path}")

if __name__ == "__main__":
    main()
