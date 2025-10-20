# App/views/__init__.py
# Import only the blueprints you actually use
from .auth_views import auth_bp
from .staff_views import staff_bp
from .index import index_views  # NEW landing page view

# This list is optional but keeps things organized
__all__ = ["auth_bp", "staff_bp", "index_views"]
