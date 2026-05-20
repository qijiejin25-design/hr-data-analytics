import os
from pathlib import Path

from flask import Flask

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET", "dev-secret-change-me"),
        MAX_CONTENT_LENGTH=32 * 1024 * 1024,
        UPLOAD_DIR=str(UPLOAD_DIR),
        EXPORT_DIR=str(EXPORT_DIR),
    )
    UPLOAD_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
