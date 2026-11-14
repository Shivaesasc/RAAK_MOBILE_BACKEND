
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Existing authentication endpoints
    path("api/auth/", include("accounts.urls")),

    # New protected User Management endpoints
    path("api/users/", include("accounts.user_management_urls")),
]
