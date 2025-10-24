# App/main.py
import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from App.models.user import User
from App.database import init_db
from App.config import load_config

# Blueprints (Views)
from App.views.auth_views import auth_bp
from App.views.staff_views import staff_bp
from App.views.admin_views import admin_bp
from App.views.system_views import system_bp
from App.views.index import index_views

def create_app(overrides: dict = None):
    """
    Application factory for the Rostering App.
    Handles configuration, DB initialization, JWT setup, and blueprint registration.
    """
    app = Flask(__name__, static_url_path="/static", template_folder="templates")

    if overrides is None:
        overrides = {}

    # Load config
    load_config(app, overrides)
    CORS(app)

    # Initialize Database
    init_db(app)

    # ----------------------------
    # JWT Configuration
    # ----------------------------
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    jwt = JWTManager(app)

    from App.database import db

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        """
        Defines what will be stored in the JWT as the identity.
        We use the userId (int) as a string.
        """
        return str(identity)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Loads the User object from the database when a JWT is presented.
        """
        identity = jwt_data["sub"]
        try:
            user_id = int(identity)
        except (TypeError, ValueError):
            return None
        return db.session.get(User, user_id)

    # ----------------------------
    # Blueprint Registration
    # ----------------------------
    app.register_blueprint(index_views)         # /
    app.register_blueprint(auth_bp)            # /admin/login, /staff/login, etc.
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(system_bp, url_prefix="/system")

    # ----------------------------
    # Protected Pages
    # ----------------------------
    @app.route('/admin/dashboard')
    @jwt_required()
    def admin_dashboard_page():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.type != "admin":
            return render_template('index.html'), 302
        return render_template('admin_dashboard.html', user=user)

    @app.route('/staff/dashboard')
    @jwt_required()
    def staff_dashboard_page():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.type != "staff":
            return render_template('index.html'), 302
        return render_template('staff_dashboard.html', user=user)

    # ----------------------------
    # Health Check
    # ----------------------------
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
