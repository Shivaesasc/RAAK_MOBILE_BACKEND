
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class UserManager(BaseUserManager):

    def create_user(self, login_id, email, full_name, password=None, **extra_fields):
        if not login_id:
            raise ValueError("Login ID is required")

        if not email:
            raise ValueError("Email is required")

        user = self.model(
            login_id=login_id.strip(),
            email=self.normalize_email(email),
            full_name=full_name,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login_id, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("user_type", "SUPER_ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Super Admin must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Super Admin must have is_superuser=True")

        return self.create_user(
            login_id,
            email,
            full_name,
            password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):

    class UserType(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMIN = "ADMIN", "Admin"
        HOD = "HOD", "HOD"
        FACULTY = "FACULTY", "Faculty"
        STUDENT = "STUDENT", "Student"

    login_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15, blank=True)

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STUDENT,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "login_id"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        db_table = "users"
        ordering = ["login_id"]

    def __str__(self):
        return f"{self.login_id} ({self.user_type})"



class UserCreationAudit(models.Model):
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="accounts_created",
    )
    created_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="creation_audit",
    )
    created_user_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "user_creation_audit"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_user.login_id} - {self.created_user_type}"
