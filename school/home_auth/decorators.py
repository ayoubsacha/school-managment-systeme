from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect("login")

            role_matches = {
                "admin": user.is_superuser or user.is_admin,
                "teacher": user.is_teacher,
                "student": user.is_student,
            }

            if any(role_matches.get(role, False) for role in roles):
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access that page.")
            return redirect("dashboard")

        return _wrapped_view

    return decorator
