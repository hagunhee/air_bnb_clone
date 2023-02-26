from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "language",
                    "gender",
                    "avatar",
                    "username",
                    "password",
                    "name",
                    "email",
                    "is_host",
                ),
            },
        ),
    )
