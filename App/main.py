# App/main.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from App.database import init_db
from App.config import load_config

# Blueprints (Views)
from App.views.auth_views import auth_bp
from App.views.staff_views import staff_bp
from App.views.index import index_views  # NEW landing page

def create_app(overrides: dict = None):
    """
    Application factory for Rostering App.
    Handles config, DB init, JWT setup, and blueprint registration.
    """
    app = Flask(__name__, static_url_path="/static", template_folder="templates")

    if overrides is None:
        overrides = {}

    # Load config and enable CORS
    load_config(app, overrides)
    CORS(app)

    # Initialize database
    init_db(app)

    # ----------------------------
    # JWT Authentication
    # ----------------------------
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        """Define how to serialize user identity into the JWT."""
        try:
            return str(identity.userId)
        except Exception:
            return str(identity)

    from App.models.user import User
    from App.database import db

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Define how to get user object from identity in JWT."""
        identity = jwt_data["sub"]
        try:
            user_id = int(identity)
        except (TypeError, ValueError):
            return None
        return db.session.get(User, user_id)

    # ----------------------------
    # Register Blueprints
    # ----------------------------
    # Landing page UI (root)
    app.register_blueprint(index_views)

    # API routes
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(staff_bp, url_prefix="/api/v1")

    # ----------------------------
    # Health Check Route
    # ----------------------------
    @app.route("/health")
    def health():
        """Basic health check endpoint."""
        return jsonify({"status": "ok"}), 200

    return app
