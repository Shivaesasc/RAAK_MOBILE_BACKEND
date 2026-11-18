from rest_framework.routers import DefaultRouter

from .views import (
    AcademicBatchViewSet,
    AcademicYearViewSet,
    CourseViewSet,
    CurriculumViewSet,
    DegreeViewSet,
    DepartmentViewSet,
    InstitutionViewSet,
    PartViewSet,
    ProgrammeViewSet,
    RegulationViewSet,
    SemesterViewSet,
    SubjectCategoryViewSet,
    SubjectViewSet,
)

router = DefaultRouter()

router.register("institutions", InstitutionViewSet, basename="institution")
router.register("departments", DepartmentViewSet, basename="department")
router.register("degrees", DegreeViewSet, basename="degree")
router.register("programmes", ProgrammeViewSet, basename="programme")
router.register("courses", CourseViewSet, basename="course")
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("academic-batches", AcademicBatchViewSet, basename="academic-batch")
router.register("semesters", SemesterViewSet, basename="semester")
router.register("regulations", RegulationViewSet, basename="regulation")
router.register("parts", PartViewSet, basename="part")
router.register("curricula", CurriculumViewSet, basename="curriculum")
router.register("subject-categories", SubjectCategoryViewSet, basename="subject-category")
router.register("subjects", SubjectViewSet, basename="subject")

urlpatterns = router.urls
