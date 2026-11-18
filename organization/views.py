from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsSuperAdmin

from .models import Department, Institution
from .pagination import OrganizationPagination
from .serializers import DepartmentSerializer, InstitutionSerializer


class OrganizationBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    pagination_class = OrganizationPagination

    http_method_names = [
        "get", "post", "put", "patch", "head", "options",
    ]

    def filter_active(self, queryset):
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
        return Response(
            {
                "detail": (
                    "Permanent deletion is disabled. "
                    "Deactivate this record instead."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

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

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(institution_type__icontains=search)
                | Q(email__icontains=search)
            )

        return self.filter_active(queryset)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        institution_id = self.request.query_params.get("institution")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(description__icontains=search)
                | Q(institution__name__icontains=search)
                | Q(institution__code__icontains=search)
            )

        if institution_id is not None:
            try:
                institution_id = int(institution_id)
                if institution_id < 1:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValidationError({
                    "institution": "Provide a valid institution ID."
                })

            queryset = queryset.filter(institution_id=institution_id)

        return self.filter_active(queryset)
