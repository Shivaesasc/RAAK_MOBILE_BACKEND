
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import serializers

from .models import User


class UserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "login_id",
            "email",
            "full_name",
            "mobile",
            "user_type",
            "password",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "is_active"]

    def validate_login_id(self, value):
        value = value.strip()

        queryset = User.objects.filter(login_id__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This Login ID already exists."
            )

        if not value:
            raise serializers.ValidationError(
                "Login ID is required."
            )

        return value

    def validate_email(self, value):
        queryset = User.objects.filter(email__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This email address already exists."
            )

        return value

    def validate_password(self, value):
        try:
            validate_password(value, user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({
                "password": "Password is required when creating a user."
            })

        if self.instance:
            request = self.context.get("request")
            new_user_type = attrs.get(
                "user_type",
                self.instance.user_type,
            )

            # Prevent changing your own account type.
            if (
                request
                and request.user.pk == self.instance.pk
                and new_user_type != self.instance.user_type
            ):
                raise serializers.ValidationError({
                    "user_type": "You cannot change your own account type."
                })

            # Do not demote the last active Super Admin.
            if (
                self.instance.user_type == "SUPER_ADMIN"
                and self.instance.is_active
                and new_user_type != "SUPER_ADMIN"
            ):
                active_super_admins = User.objects.filter(
                    user_type="SUPER_ADMIN",
                    is_active=True,
                ).count()

                if active_super_admins <= 1:
                    raise serializers.ValidationError({
                        "user_type": "At least one active Super Admin must remain."
                    })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )

    def update(self, instance, validated_data):
        # Password changes must use the dedicated reset-password API.
        validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance
