from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, PasswordResetRequest


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "is_admin", "is_teacher", "is_student")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name", "username")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Roles",
            {"fields": ("is_admin", "is_teacher", "is_student", "is_authorized")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_admin",
                    "is_teacher",
                    "is_student",
                ),
            },
        ),
    )


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "created_at")
    search_fields = ("email", "user__email")
    ordering = ("-created_at",)
