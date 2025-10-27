"""Web-facing interfaces wrapping CLI capabilities."""

from .api.app import app as api_app

__all__ = ["api_app"]
