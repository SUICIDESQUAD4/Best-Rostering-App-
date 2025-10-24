# App/views/__init__.py
from .auth_views import auth_bp
from .staff_views import staff_bp
from .admin_views import admin_bp
from .index import index_views
from .system_views import system_bp

__all__ = ["auth_bp", "staff_bp", "admin_bp", "system_bp", "index_views"]
