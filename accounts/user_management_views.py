
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import User, UserCreationAudit
from .permissions import IsSuperAdmin
from .user_management_serializers import UserManagementSerializer


class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserManagementSerializer
    permission_classes = [IsSuperAdmin]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    queryset = User.objects.all().order_by("-date_joined")

    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.query_params.get("search", "").strip()
        user_type = self.request.query_params.get("user_type")
        active = self.request.query_params.get("is_active")

        if search:
            queryset = queryset.filter(
                Q(login_id__icontains=search)
                | Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(mobile__icontains=search)
            )

        if user_type:
            valid_types = User.UserType.values

            if user_type not in valid_types:
                raise ValidationError({
                    "user_type": "Invalid user type."
                })

            queryset = queryset.filter(user_type=user_type)

        if active is not None:
            if active.lower() not in ("true", "false"):
                raise ValidationError({
                    "is_active": "Use true or false."
                })

            queryset = queryset.filter(
                is_active=(active.lower() == "true")
            )

        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            created_user = serializer.save()

            UserCreationAudit.objects.create(
                created_by=self.request.user,
                created_user=created_user,
                created_user_type=created_user.user_type,
                remarks="Created through Mobile ERP User Management",
            )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "User deletion is disabled. Deactivate the account instead."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({
            "detail": "User activated successfully.",
            "id": user.id,
            "is_active": user.is_active,
        })


    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()

        if user.pk == request.user.pk:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.user_type == "SUPER_ADMIN" and user.is_active:
            active_super_admins = User.objects.filter(
                user_type="SUPER_ADMIN",
                is_active=True,
            ).count()

            if active_super_admins <= 1:
                return Response(
                    {"detail": "At least one active Super Admin must remain."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response({
            "detail": "User deactivated successfully.",
            "id": user.id,
            "is_active": user.is_active,
        })


    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get("new_password")

        if not isinstance(new_password, str) or not new_password:
            return Response(
                {"new_password": "A new password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except Exception as exc:
            messages = (
                exc.messages
                if hasattr(exc, "messages")
                else ["Password validation failed."]
            )
            return Response(
                {"new_password": messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({
            "detail": "Password reset successfully.",
            "id": user.id,
        })
