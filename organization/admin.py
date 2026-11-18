from django.contrib import admin
from .models import Institution, Department


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "institution_type",
        "phone",
        "is_active",
    )
    list_filter = ("is_active", "institution_type")
    search_fields = ("name", "code", "email")
    ordering = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "institution",
        "phone",
        "is_active",
    )
    list_filter = ("institution", "is_active")
    search_fields = (
        "name",
        "code",
        "institution__name",
    )
    ordering = ("institution__name", "name")
