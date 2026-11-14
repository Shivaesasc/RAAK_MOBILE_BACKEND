
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    message = "Only an active Super Admin can manage users."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.user_type == "SUPER_ADMIN"
            and user.is_superuser
        )
