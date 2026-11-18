from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, InstitutionViewSet

router = DefaultRouter()
router.register("institutions", InstitutionViewSet, basename="institution")
router.register("departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls
