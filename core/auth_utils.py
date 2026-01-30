"""
Session-based auth for MongoDB users (no Django User model for main app).
"""
from functools import wraps
from django.shortcuts import redirect
from .mongodb import users_collection, to_object_id


def get_current_user(request):
    """Return user dict from MongoDB by session user_id, or None."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    uid = to_object_id(user_id)
    if not uid:
        return None
    user = users_collection().find_one({"_id": uid})
    if user:
        user["id"] = str(user["_id"])
    return user


def login_required_mongo(view_func):
    """Decorator: redirect to login if user not in session (MongoDB user)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("user_id"):
            from django.urls import reverse
            next_url = request.get_full_path()
            return redirect(f"{reverse('users:login')}?next={next_url}")
        return view_func(request, *args, **kwargs)
    return _wrapped
