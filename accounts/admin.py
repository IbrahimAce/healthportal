"""
Admin configuration for the User model.
Customised list display so staff can quickly see roles and status.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ("email", "get_full_name", "role", "is_active", "date_joined")
    list_filter   = ("role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering      = ("-date_joined",)

    fieldsets = (
        ("Login Info",   {"fields": ("email", "password")}),
        ("Personal",     {"fields": ("first_name", "last_name", "phone")}),
        ("Role & Access",{"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Permissions",  {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )
