from django.contrib import admin

from .models import (
    AcademicBatch,
    AcademicYear,
    Course,
    Curriculum,
    Degree,
    Department,
    Institution,
    Part,
    Programme,
    Regulation,
    Semester,
    Subject,
    SubjectCategory,
)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution_type", "phone", "is_active")
    list_filter = ("is_active", "institution_type")
    search_fields = ("name", "code", "email")
    ordering = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution", "phone", "is_active")
    list_filter = ("institution", "is_active")
    search_fields = ("name", "code", "institution__name")
    ordering = ("institution__name", "name")


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution", "duration_years", "is_active")
    list_filter = ("institution", "is_active")
    search_fields = ("name", "code", "institution__name")


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "degree", "department", "total_semesters", "is_active")
    list_filter = ("degree", "department", "is_active")
    search_fields = ("name", "code", "degree__name", "department__name")


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution", "start_date", "end_date", "is_active")
    list_filter = ("institution", "is_active")
    search_fields = ("name", "code")


@admin.register(AcademicBatch)
class AcademicBatchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "programme", "academic_year", "admission_year", "completion_year", "is_active")
    list_filter = ("programme", "academic_year", "is_active")
    search_fields = ("name", "code", "programme__name")


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "programme", "semester_number", "is_active")
    list_filter = ("programme", "is_active")
    search_fields = ("name", "programme__name")


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "programme", "effective_from", "effective_to", "is_active")
    list_filter = ("programme", "is_active")
    search_fields = ("name", "code", "programme__name")


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "programme", "semester", "part_number", "is_active")
    list_filter = ("programme", "semester", "is_active")
    search_fields = ("name", "programme__name")


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "institution", "is_active")
    list_filter = ("institution", "is_active")
    search_fields = ("name", "code")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "programme", "semester", "part", "credits", "is_active")
    list_filter = ("programme", "semester", "subject_category", "is_active")
    search_fields = ("name", "code", "programme__name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "programme", "subject_category", "credits", "is_active")
    list_filter = ("programme", "subject_category", "is_active")
    search_fields = ("name", "code", "programme__name")


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "programme", "regulation", "semester", "part", "is_active")
    list_filter = ("programme", "regulation", "semester", "is_active")
    search_fields = ("name", "code", "programme__name")
    filter_horizontal = ("courses", "subjects")
