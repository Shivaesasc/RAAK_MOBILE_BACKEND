from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from .models import (
    Institution,
    Department,
    Degree,
    Programme,
    Course,
    AcademicYear,
    AcademicBatch,
    Semester,
    Regulation,
    Part,
    Curriculum,
    SubjectCategory,
    Subject,
)


class OrganizationAPITests(APITestCase):
    """
    Organization API integration tests.
    Runs with config.test_settings and an in-memory SQLite database.
    """

    def setUp(self):
        self.admin = User.objects.create_superuser(
            login_id="organization-test-admin",
            email="organization-test-admin@example.test",
            full_name="Organization Test Admin",
            password="TestPassword@123",
        )

        token = RefreshToken.for_user(self.admin).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        # Base institution and academic structure.
        self.institution = Institution.objects.create(
            name="Test Institution",
            code="TEST-INST",
        )

        self.department = Department.objects.create(
            institution=self.institution,
            name="Computer Science",
            code="TEST-CS",
        )

        self.degree = Degree.objects.create(
            institution=self.institution,
            name="Bachelor of Science",
            code="TEST-BSC",
            level="UG",
            duration_years=3,
        )

        self.programme = Programme.objects.create(
            degree=self.degree,
            department=self.department,
            name="Computer Science",
            code="TEST-BSC-CS",
            duration_years=3,
            total_semesters=6,
        )

        self.academic_year = AcademicYear.objects.create(
            institution=self.institution,
            name="2026-2027",
            code="TEST-AY-2026",
            start_date=date(2026, 6, 1),
            end_date=date(2027, 5, 31),
        )

        self.academic_batch = AcademicBatch.objects.create(
            programme=self.programme,
            academic_year=self.academic_year,
            name="2026 Admission",
            code="TEST-BATCH-2026",
            admission_year=2026,
            completion_year=2029,
        )

        self.semester = Semester.objects.create(
            programme=self.programme,
            semester_number=1,
            name="Semester I",
        )

        self.regulation = Regulation.objects.create(
            programme=self.programme,
            name="Test Regulation 2026",
            code="TEST-REG-2026",
            effective_from=date(2026, 6, 1),
            description="Test regulation",
        )

        self.part = Part.objects.create(
            programme=self.programme,
            semester=self.semester,
            name="Part I",
            part_number=1,
            description="Test part",
        )

        self.subject_category = SubjectCategory.objects.create(
            institution=self.institution,
            name="Core",
            code="TEST-CORE",
            description="Core subjects",
        )

        self.course = Course.objects.create(
            programme=self.programme,
            semester=self.semester,
            part=self.part,
            subject_category=self.subject_category,
            name="Programming Fundamentals",
            code="TEST-COURSE-01",
            credits=4,
            contact_hours=60,
            description="Test course",
        )

        self.subject = Subject.objects.create(
            programme=self.programme,
            subject_category=self.subject_category,
            name="Programming",
            code="TEST-SUBJECT-01",
            credits=4,
            description="Test subject",
        )

        self.curriculum = Curriculum.objects.create(
            programme=self.programme,
            regulation=self.regulation,
            semester=self.semester,
            part=self.part,
            name="Test Curriculum",
            code="TEST-CURR-01",
            effective_from=date(2026, 6, 1),
            description="Test curriculum",
        )
        self.curriculum.courses.add(self.course)
        self.curriculum.subjects.add(self.subject)

    def endpoint(self, route, record_id=None):
        if record_id is None:
            return f"/api/organization/{route}/"
        return f"/api/organization/{route}/{record_id}/"

    def test_all_thirteen_list_endpoints_require_super_admin(self):
        routes = [
            "institutions",
            "departments",
            "degrees",
            "programmes",
            "courses",
            "academic-years",
            "academic-batches",
            "semesters",
            "regulations",
            "parts",
            "curricula",
            "subject-categories",
            "subjects",
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(self.endpoint(route))
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    response.data,
                )

    def test_all_thirteen_detail_endpoints(self):
        records = [
            ("institutions", self.institution),
            ("departments", self.department),
            ("degrees", self.degree),
            ("programmes", self.programme),
            ("courses", self.course),
            ("academic-years", self.academic_year),
            ("academic-batches", self.academic_batch),
            ("semesters", self.semester),
            ("regulations", self.regulation),
            ("parts", self.part),
            ("curricula", self.curriculum),
            ("subject-categories", self.subject_category),
            ("subjects", self.subject),
        ]

        for route, record in records:
            with self.subTest(route=route):
                response = self.client.get(
                    self.endpoint(route, record.pk)
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    response.data,
                )
                self.assertEqual(response.data["id"], record.pk)

    def test_search_and_active_filter(self):
        response = self.client.get(
            self.endpoint("institutions"),
            {"search": "Test Institution"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

        response = self.client.get(
            self.endpoint("institutions"),
            {"is_active": "true"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.endpoint("institutions"),
            {"is_active": "invalid"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_foreign_key_filter(self):
        response = self.client.get(
            self.endpoint("departments"),
            {"institution": self.institution.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(
                item["id"] == self.department.pk
                for item in response.data["results"]
            )
        )

    def test_invalid_foreign_key_filter_is_rejected(self):
        response = self.client.get(
            self.endpoint("departments"),
            {"institution": "invalid"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_pagination_page_size(self):
        response = self.client.get(
            self.endpoint("institutions"),
            {"page_size": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_department(self):
        response = self.client.patch(
            self.endpoint("departments", self.department.pk),
            {"name": "Updated Computer Science"},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.department.refresh_from_db()
        self.assertEqual(
            self.department.name,
            "Updated Computer Science",
        )

    def test_create_department(self):
        response = self.client.post(
            self.endpoint("departments"),
            {
                "institution": self.institution.pk,
                "name": "Information Technology",
                "code": "TEST-IT",
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )
        self.assertTrue(
            Department.objects.filter(code="TEST-IT").exists()
        )

    def test_duplicate_department_code_is_rejected(self):
        response = self.client.post(
            self.endpoint("departments"),
            {
                "institution": self.institution.pk,
                "name": "Another Department",
                "code": self.department.code,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_programme_rejects_degree_and_department_from_different_institutions(self):
        another_institution = Institution.objects.create(
            name="Another Test Institution",
            code="TEST-INST-2",
        )
        another_department = Department.objects.create(
            institution=another_institution,
            name="Other Department",
            code="TEST-OTHER",
        )

        response = self.client.post(
            self.endpoint("programmes"),
            {
                "degree": self.degree.pk,
                "department": another_department.pk,
                "name": "Invalid Programme",
                "code": "TEST-INVALID-PROG",
                "duration_years": 3,
                "total_semesters": 6,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_semester_rejects_number_above_programme_limit(self):
        response = self.client.post(
            self.endpoint("semesters"),
            {
                "programme": self.programme.pk,
                "semester_number": 7,
                "name": "Semester VII",
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_protected_institution_delete_returns_conflict(self):
        response = self.client.delete(
            self.endpoint("institutions", self.institution.pk)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )
        self.assertTrue(
            Institution.objects.filter(pk=self.institution.pk).exists()
        )

    def test_department_deactivate_then_institution_deactivate(self):
        response = self.client.post(
            self.endpoint("institutions", self.institution.pk)
            + "deactivate/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        response = self.client.post(
            self.endpoint("departments", self.department.pk)
            + "deactivate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Degree is also a direct child of Institution.
        response = self.client.post(
            self.endpoint("degrees", self.degree.pk)
            + "deactivate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.endpoint("institutions", self.institution.pk)
            + "deactivate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.institution.refresh_from_db()
        self.assertFalse(self.institution.is_active)

    def test_activate_endpoint(self):
        self.department.is_active = False
        self.department.save()

        response = self.client.post(
            self.endpoint("departments", self.department.pk)
            + "activate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.department.refresh_from_db()
        self.assertTrue(self.department.is_active)

    def test_unauthenticated_request_is_rejected(self):
        self.client.credentials()
        response = self.client.get(self.endpoint("institutions"))
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_non_super_admin_is_rejected(self):
        ordinary_user = User.objects.create_user(
            login_id="organization-test-user",
            email="organization-test-user@example.test",
            full_name="Ordinary Test User",
            password="TestPassword@123",
            user_type="ADMIN",
        )

        token = RefreshToken.for_user(ordinary_user).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.get(self.endpoint("institutions"))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_curriculum_relationships(self):
        response = self.client.get(
            self.endpoint("curricula", self.curriculum.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(self.course.pk, response.data["courses"])
        self.assertIn(self.subject.pk, response.data["subjects"])

    def test_delete_unreferenced_leaf_records(self):
        # Create independent records and verify DELETE.
        extra_subject = Subject.objects.create(
            programme=self.programme,
            subject_category=self.subject_category,
            name="Temporary Subject",
            code="TEST-TEMP-SUB",
            credits=2,
            description="Temporary",
        )

        response = self.client.delete(
            self.endpoint("subjects", extra_subject.pk)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Subject.objects.filter(pk=extra_subject.pk).exists()
        )
