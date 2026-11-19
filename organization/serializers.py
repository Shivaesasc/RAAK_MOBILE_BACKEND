from rest_framework import serializers

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


def get_value(attrs, instance, field):
    if field in attrs:
        return attrs[field]
    return getattr(instance, field, None) if instance else None


def require_active(record, field_name):
    if record is not None and not record.is_active:
        raise serializers.ValidationError({
            field_name: "Select an active record."
        })


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
        source="institution.name", read_only=True
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
        require_active(institution, "institution")
        return institution


class DegreeSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(
        source="institution.name", read_only=True
    )

    class Meta:
        model = Degree
        fields = [
            "id", "institution", "institution_name", "name", "code",
            "level", "duration_years", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "institution_name", "created_at", "updated_at",
        ]

    def validate_institution(self, institution):
        require_active(institution, "institution")
        return institution


class ProgrammeSerializer(serializers.ModelSerializer):
    degree_name = serializers.CharField(source="degree.name", read_only=True)
    department_name = serializers.CharField(
        source="department.name", read_only=True
    )

    class Meta:
        model = Programme
        fields = [
            "id", "degree", "degree_name", "department",
            "department_name", "name", "code", "duration_years",
            "total_semesters", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "degree_name", "department_name",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        degree = get_value(attrs, self.instance, "degree")
        department = get_value(attrs, self.instance, "department")
        require_active(degree, "degree")
        require_active(department, "department")

        # Degree and Department are independent children of Institution.
        # A Programme may link them only when they belong to the same Institution.
        if degree and department and degree.institution_id != department.institution_id:
            raise serializers.ValidationError({
                "department": (
                    "The selected Department and Degree must belong to the same Institution."
                )
            })
        return attrs


class AcademicYearSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(
        source="institution.name", read_only=True
    )

    class Meta:
        model = AcademicYear
        fields = [
            "id", "institution", "institution_name", "name", "code",
            "start_date", "end_date", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "institution_name", "created_at", "updated_at",
        ]

    def validate(self, attrs):
        institution = get_value(attrs, self.instance, "institution")
        start_date = get_value(attrs, self.instance, "start_date")
        end_date = get_value(attrs, self.instance, "end_date")
        require_active(institution, "institution")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be later than start date."
            })
        return attrs


class AcademicBatchSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )
    academic_year_name = serializers.CharField(
        source="academic_year.name", read_only=True
    )

    class Meta:
        model = AcademicBatch
        fields = [
            "id", "programme", "programme_name",
            "academic_year", "academic_year_name",
            "name", "code", "admission_year", "completion_year",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "academic_year_name",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        academic_year = get_value(attrs, self.instance, "academic_year")
        admission = get_value(attrs, self.instance, "admission_year")
        completion = get_value(attrs, self.instance, "completion_year")
        require_active(programme, "programme")
        require_active(academic_year, "academic_year")

        if programme and academic_year:
            institution_id = programme.department.institution_id
            if academic_year.institution_id != institution_id:
                raise serializers.ValidationError({
                    "academic_year": "Academic Year must belong to the Programme's institution."
                })

        if admission and completion and completion <= admission:
            raise serializers.ValidationError({
                "completion_year": "Completion year must be later than admission year."
            })
        return attrs


class SemesterSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )

    class Meta:
        model = Semester
        fields = [
            "id", "programme", "programme_name",
            "semester_number", "name", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "created_at", "updated_at",
        ]

    def validate_programme(self, programme):
        require_active(programme, "programme")
        return programme

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        number = get_value(attrs, self.instance, "semester_number")
        if programme and number and number > programme.total_semesters:
            raise serializers.ValidationError({
                "semester_number": (
                    f"This Programme has {programme.total_semesters} semesters."
                )
            })
        return attrs


class RegulationSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )

    class Meta:
        model = Regulation
        fields = [
            "id", "programme", "programme_name", "name", "code",
            "effective_from", "effective_to", "description",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "created_at", "updated_at",
        ]

    def validate_programme(self, programme):
        require_active(programme, "programme")
        return programme

    def validate(self, attrs):
        start = get_value(attrs, self.instance, "effective_from")
        end = get_value(attrs, self.instance, "effective_to")
        if start and end and end < start:
            raise serializers.ValidationError({
                "effective_to": "Effective-to date cannot be earlier than effective-from date."
            })
        return attrs


class PartSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )
    semester_name = serializers.CharField(
        source="semester.name", read_only=True
    )

    class Meta:
        model = Part
        fields = [
            "id", "programme", "programme_name",
            "semester", "semester_name", "name",
            "part_number", "description", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "semester_name",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        semester = get_value(attrs, self.instance, "semester")
        require_active(programme, "programme")
        require_active(semester, "semester")

        if programme and semester and semester.programme_id != programme.id:
            raise serializers.ValidationError({
                "semester": "Semester must belong to the selected Programme."
            })
        return attrs


class SubjectCategorySerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(
        source="institution.name", read_only=True
    )

    class Meta:
        model = SubjectCategory
        fields = [
            "id", "institution", "institution_name", "name",
            "code", "description", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "institution_name", "created_at", "updated_at",
        ]

    def validate_institution(self, institution):
        require_active(institution, "institution")
        return institution


class CourseSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )
    semester_name = serializers.CharField(
        source="semester.name", read_only=True
    )
    part_name = serializers.CharField(source="part.name", read_only=True)
    subject_category_name = serializers.CharField(
        source="subject_category.name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id", "programme", "programme_name",
            "semester", "semester_name", "part", "part_name",
            "subject_category", "subject_category_name",
            "name", "code", "credits", "contact_hours",
            "description", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "semester_name", "part_name",
            "subject_category_name", "created_at", "updated_at",
        ]

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        semester = get_value(attrs, self.instance, "semester")
        part = get_value(attrs, self.instance, "part")
        category = get_value(attrs, self.instance, "subject_category")

        for field, record in [
            ("programme", programme), ("semester", semester),
            ("part", part), ("subject_category", category),
        ]:
            require_active(record, field)

        if programme and semester and semester.programme_id != programme.id:
            raise serializers.ValidationError({
                "semester": "Semester must belong to the selected Programme."
            })
        if programme and part and part.programme_id != programme.id:
            raise serializers.ValidationError({
                "part": "Part must belong to the selected Programme."
            })
        if semester and part and part.semester_id != semester.id:
            raise serializers.ValidationError({
                "part": "Part must belong to the selected Semester."
            })
        if programme and category:
            institution_id = programme.department.institution_id
            if category.institution_id != institution_id:
                raise serializers.ValidationError({
                    "subject_category": "Subject Category must belong to the Programme's institution."
                })
        return attrs


class SubjectSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )
    subject_category_name = serializers.CharField(
        source="subject_category.name", read_only=True
    )

    class Meta:
        model = Subject
        fields = [
            "id", "programme", "programme_name",
            "subject_category", "subject_category_name",
            "name", "code", "credits", "description",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "subject_category_name",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        category = get_value(attrs, self.instance, "subject_category")
        require_active(programme, "programme")
        require_active(category, "subject_category")

        if programme and category:
            if category.institution_id != programme.department.institution_id:
                raise serializers.ValidationError({
                    "subject_category": "Subject Category must belong to the Programme's institution."
                })
        return attrs


class CurriculumSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True
    )
    regulation_name = serializers.CharField(
        source="regulation.name", read_only=True
    )
    semester_name = serializers.CharField(
        source="semester.name", read_only=True
    )
    part_name = serializers.CharField(source="part.name", read_only=True)
    courses = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Course.objects.all(), required=False
    )
    subjects = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Subject.objects.all(), required=False
    )

    class Meta:
        model = Curriculum
        fields = [
            "id", "programme", "programme_name",
            "regulation", "regulation_name",
            "semester", "semester_name", "part", "part_name",
            "name", "code", "courses", "subjects",
            "effective_from", "description", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "programme_name", "regulation_name",
            "semester_name", "part_name",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        programme = get_value(attrs, self.instance, "programme")
        regulation = get_value(attrs, self.instance, "regulation")
        semester = get_value(attrs, self.instance, "semester")
        part = get_value(attrs, self.instance, "part")

        for field, record in [
            ("programme", programme), ("regulation", regulation),
            ("semester", semester), ("part", part),
        ]:
            require_active(record, field)

        if programme and regulation and regulation.programme_id != programme.id:
            raise serializers.ValidationError({
                "regulation": "Regulation must belong to the selected Programme."
            })
        if programme and semester and semester.programme_id != programme.id:
            raise serializers.ValidationError({
                "semester": "Semester must belong to the selected Programme."
            })
        if programme and part and part.programme_id != programme.id:
            raise serializers.ValidationError({
                "part": "Part must belong to the selected Programme."
            })
        if semester and part and part.semester_id != semester.id:
            raise serializers.ValidationError({
                "part": "Part must belong to the selected Semester."
            })

        selected_courses = attrs.get("courses")
        if selected_courses is None and self.instance:
            selected_courses = list(self.instance.courses.all())
        if programme and selected_courses:
            invalid = [c.id for c in selected_courses if c.programme_id != programme.id]
            if invalid:
                raise serializers.ValidationError({
                    "courses": f"These courses do not belong to the selected Programme: {invalid}"
                })
            if semester and any(c.semester_id != semester.id for c in selected_courses):
                raise serializers.ValidationError({
                    "courses": "All selected Courses must belong to the selected Semester."
                })
            if part and any(c.part_id != part.id for c in selected_courses):
                raise serializers.ValidationError({
                    "courses": "All selected Courses must belong to the selected Part."
                })

        selected_subjects = attrs.get("subjects")
        if selected_subjects is None and self.instance:
            selected_subjects = list(self.instance.subjects.all())
        if programme and selected_subjects:
            invalid = [s.id for s in selected_subjects if s.programme_id != programme.id]
            if invalid:
                raise serializers.ValidationError({
                    "subjects": f"These subjects do not belong to the selected Programme: {invalid}"
                })

        return attrs
