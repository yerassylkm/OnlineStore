"""
Context processors for templates.
"""
from .auth_utils import get_current_user


def current_user(request):
    """Add current_user from MongoDB session to template context."""
    return {"current_user": get_current_user(request)}
