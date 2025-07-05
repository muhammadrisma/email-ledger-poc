"""
Email Ledger API Package.

Contains FastAPI application and routes for the REST API.
"""

from .app import app, create_app
from .routes import router

__all__ = [
    "app",
    "create_app", 
    "router",
] 