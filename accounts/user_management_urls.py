
from rest_framework.routers import DefaultRouter

from .user_management_views import UserManagementViewSet

router = DefaultRouter()
router.register("", UserManagementViewSet, basename="user-management")

urlpatterns = router.urls
