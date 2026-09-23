from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for TechBlogKe users."""

    model = CustomUser

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
        "updated_at",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "TechBlogKe profile",
            {
                "fields": (
                    "role",
                    "bio",
                    "profile_image",
                    "website",
                    "updated_at",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Account information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                ),
            },
        ),
    )