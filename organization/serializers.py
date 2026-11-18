from rest_framework import serializers

from .models import Department, Institution


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            "id", "name", "code", "institution_type",
            "email", "phone", "website", "address",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DepartmentSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(
        source="institution.name",
        read_only=True,
    )

    class Meta:
        model = Department
        fields = [
            "id", "institution", "institution_name",
            "name", "code", "description", "email",
            "phone", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "institution_name", "created_at", "updated_at",
        ]

    def validate_institution(self, institution):
        if not institution.is_active:
            raise serializers.ValidationError(
                "Select an active institution."
            )
        return institution
