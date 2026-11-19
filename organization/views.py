from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsSuperAdmin

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
from .pagination import OrganizationPagination
from .serializers import (
    AcademicBatchSerializer,
    AcademicYearSerializer,
    CourseSerializer,
    CurriculumSerializer,
    DegreeSerializer,
    DepartmentSerializer,
    InstitutionSerializer,
    PartSerializer,
    ProgrammeSerializer,
    RegulationSerializer,
    SemesterSerializer,
    SubjectSerializer,
    SubjectCategorySerializer,
)


class OrganizationBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    pagination_class = OrganizationPagination

    http_method_names = [
        "get", "post", "put", "patch", "delete", "head", "options",
    ]

    search_fields = ()
    filter_fields = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()

        if search and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(condition)

        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value is not None:
                try:
                    record_id = int(value)
                    if record_id < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    raise ValidationError({
                        field: "Provide a valid positive ID."
                    })
                queryset = queryset.filter(**{f"{field}_id": record_id})

        active = self.request.query_params.get("is_active")
        if active is not None:
            value = active.lower()
            if value not in ("true", "false"):
                raise ValidationError({
                    "is_active": "Use true or false."
                })
            queryset = queryset.filter(is_active=(value == "true"))

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        record_id = instance.pk

        try:
            instance.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This record cannot be deleted because other records "
                        "are linked to it. Remove or reassign those relationships first."
                    ),
                    "id": record_id,
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = True
        instance.save(update_fields=["is_active", "updated_at"])
        return Response({
            "detail": "Record activated successfully.",
            "id": instance.pk,
            "is_active": True,
        })

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return Response({
            "detail": "Record deactivated successfully.",
            "id": instance.pk,
            "is_active": False,
        })


class InstitutionViewSet(OrganizationBaseViewSet):
    serializer_class = InstitutionSerializer
    queryset = Institution.objects.all().order_by("name")
    search_fields = ("name", "code", "institution_type", "email")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, *args, **kwargs):
        institution = self.get_object()

        if institution.departments.filter(is_active=True).exists():
            return Response(
                {
                    "detail": (
                        "Deactivate the institution's active departments "
                        "before deactivating this institution."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if institution.degrees.filter(is_active=True).exists():
            return Response(
                {
                    "detail": (
                        "Deactivate the institution's active degrees "
                        "before deactivating this institution."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        institution.is_active = False
        institution.save(update_fields=["is_active", "updated_at"])

        return Response({
            "detail": "Institution deactivated successfully.",
            "id": institution.pk,
            "is_active": False,
        })


class DepartmentViewSet(OrganizationBaseViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.select_related(
        "institution"
    ).all().order_by("institution__name", "name")
    search_fields = (
        "name", "code", "description",
        "institution__name", "institution__code",
    )
    filter_fields = ("institution",)


class DegreeViewSet(OrganizationBaseViewSet):
    serializer_class = DegreeSerializer
    queryset = Degree.objects.select_related("institution").all()
    search_fields = ("name", "code", "level", "institution__name")
    filter_fields = ("institution",)


class ProgrammeViewSet(OrganizationBaseViewSet):
    serializer_class = ProgrammeSerializer
    queryset = Programme.objects.select_related(
        "degree", "department"
    ).all()
    search_fields = (
        "name", "code", "degree__name", "department__name",
    )
    filter_fields = ("degree", "department")


class AcademicYearViewSet(OrganizationBaseViewSet):
    serializer_class = AcademicYearSerializer
    queryset = AcademicYear.objects.select_related("institution").all()
    search_fields = ("name", "code", "institution__name")
    filter_fields = ("institution",)


class AcademicBatchViewSet(OrganizationBaseViewSet):
    serializer_class = AcademicBatchSerializer
    queryset = AcademicBatch.objects.select_related(
        "programme", "academic_year"
    ).all()
    search_fields = (
        "name", "code", "programme__name", "academic_year__name",
    )
    filter_fields = ("programme", "academic_year")


class SemesterViewSet(OrganizationBaseViewSet):
    serializer_class = SemesterSerializer
    queryset = Semester.objects.select_related("programme").all()
    search_fields = ("name", "programme__name", "programme__code")
    filter_fields = ("programme",)


class RegulationViewSet(OrganizationBaseViewSet):
    serializer_class = RegulationSerializer
    queryset = Regulation.objects.select_related("programme").all()
    search_fields = ("name", "code", "programme__name")
    filter_fields = ("programme",)


class PartViewSet(OrganizationBaseViewSet):
    serializer_class = PartSerializer
    queryset = Part.objects.select_related(
        "programme", "semester"
    ).all()
    search_fields = (
        "name", "programme__name", "semester__name",
    )
    filter_fields = ("programme", "semester")


class CourseViewSet(OrganizationBaseViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.select_related(
        "programme", "semester", "part", "subject_category"
    ).all()
    search_fields = (
        "name", "code", "programme__name",
        "semester__name", "part__name",
        "subject_category__name",
    )
    filter_fields = (
        "programme", "semester", "part", "subject_category",
    )


class SubjectCategoryViewSet(OrganizationBaseViewSet):
    serializer_class = SubjectCategorySerializer
    queryset = SubjectCategory.objects.select_related("institution").all()
    search_fields = ("name", "code", "institution__name")
    filter_fields = ("institution",)


class SubjectViewSet(OrganizationBaseViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.select_related(
        "programme", "subject_category"
    ).all()
    search_fields = (
        "name", "code", "programme__name",
        "subject_category__name",
    )
    filter_fields = ("programme", "subject_category")


class CurriculumViewSet(OrganizationBaseViewSet):
    serializer_class = CurriculumSerializer
    queryset = Curriculum.objects.select_related(
        "programme", "regulation", "semester", "part"
    ).prefetch_related("courses", "subjects").all()
    search_fields = (
        "name", "code", "programme__name",
        "regulation__name", "semester__name", "part__name",
    )
    filter_fields = ("programme", "regulation", "semester", "part")
