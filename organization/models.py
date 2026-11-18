from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True)
    institution_type = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization_institutions"
        ordering = ["name"]
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(models.Model):
    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="departments",
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization_departments"
        ordering = ["institution__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "code"],
                name="unique_department_code_per_institution",
            ),
            models.UniqueConstraint(
                fields=["institution", "name"],
                name="unique_department_name_per_institution",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
