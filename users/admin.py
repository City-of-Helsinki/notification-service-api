from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "id",
        "uuid",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
        "last_login",
    )
    fieldsets = DjangoUserAdmin.fieldsets + (("UUID", {"fields": ("uuid",)}),)
    readonly_fields = ("uuid",)
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "date_joined",
        "last_login",
    )
    search_fields = DjangoUserAdmin.search_fields + ("uuid",)
    date_hierarchy = "date_joined"
