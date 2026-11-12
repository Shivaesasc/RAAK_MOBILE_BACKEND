
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MobileLoginView,
    CurrentUserView,
    MobileLogoutView,
)

urlpatterns = [
    path("login/", MobileLoginView.as_view(), name="mobile-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("logout/", MobileLogoutView.as_view(), name="mobile-logout"),
]
