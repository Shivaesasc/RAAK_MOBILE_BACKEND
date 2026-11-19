from django.db import models


class TimeStampedModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Institution(TimeStampedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True)
    institution_type = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        db_table = "organization_institutions"
        ordering = ["name"]
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(TimeStampedModel):
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="departments"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

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



class Degree(TimeStampedModel):
    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="degrees",
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    level = models.CharField(max_length=50, blank=True)
    duration_years = models.PositiveSmallIntegerField(default=3)

    class Meta:
        db_table = "organization_degrees"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "code"],
                name="unique_degree_code_per_institution",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"



class Programme(TimeStampedModel):
    degree = models.ForeignKey(
        Degree, on_delete=models.PROTECT, related_name="programmes"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="programmes"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    duration_years = models.PositiveSmallIntegerField(default=3)
    total_semesters = models.PositiveSmallIntegerField(default=6)

    class Meta:
        db_table = "organization_programmes"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "code"],
                name="unique_programme_code_per_department",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="courses"
    )
    semester = models.ForeignKey(
        "Semester", on_delete=models.PROTECT, related_name="courses"
    )
    part = models.ForeignKey(
        "Part", on_delete=models.PROTECT, related_name="courses"
    )
    subject_category = models.ForeignKey(
        "SubjectCategory", on_delete=models.PROTECT, related_name="courses"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contact_hours = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_courses"
        ordering = ["programme__name", "semester__semester_number", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "code"],
                name="unique_course_code_per_programme",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicYear(TimeStampedModel):
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="academic_years"
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "organization_academic_years"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "code"],
                name="unique_academic_year_code_per_institution",
            )
        ]

    def __str__(self):
        return self.name


class AcademicBatch(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="academic_batches"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name="academic_batches"
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    admission_year = models.PositiveSmallIntegerField()
    completion_year = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "organization_academic_batches"
        ordering = ["-admission_year", "programme__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "code"],
                name="unique_batch_code_per_programme",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.programme.name}"


class Semester(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="semesters"
    )
    semester_number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "organization_semesters"
        ordering = ["programme__name", "semester_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "semester_number"],
                name="unique_semester_per_programme",
            )
        ]

    def __str__(self):
        return self.name or f"Semester {self.semester_number}"


class Regulation(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="regulations"
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_regulations"
        ordering = ["-effective_from"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "code"],
                name="unique_regulation_code_per_programme",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Part(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="parts"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name="parts"
    )
    name = models.CharField(max_length=100)
    part_number = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_parts"
        ordering = ["programme__name", "semester__semester_number", "part_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["semester", "part_number"],
                name="unique_part_number_per_semester",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.semester}"


class SubjectCategory(TimeStampedModel):
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="subject_categories"
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_subject_categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "code"],
                name="unique_subject_category_code_per_institution",
            )
        ]

    def __str__(self):
        return self.name


class Subject(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="subjects"
    )
    subject_category = models.ForeignKey(
        SubjectCategory, on_delete=models.PROTECT, related_name="subjects"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_subjects"
        ordering = ["programme__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "code"],
                name="unique_subject_code_per_programme",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Curriculum(TimeStampedModel):
    programme = models.ForeignKey(
        Programme, on_delete=models.PROTECT, related_name="curricula"
    )
    regulation = models.ForeignKey(
        Regulation, on_delete=models.PROTECT, related_name="curricula"
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name="curricula"
    )
    part = models.ForeignKey(
        Part, on_delete=models.PROTECT, related_name="curricula"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)
    courses = models.ManyToManyField(Course, blank=True, related_name="curricula")
    subjects = models.ManyToManyField(Subject, blank=True, related_name="curricula")
    effective_from = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "organization_curricula"
        ordering = ["programme__name", "semester__semester_number", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "regulation", "semester", "part", "code"],
                name="unique_curriculum_code_per_structure",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
