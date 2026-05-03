"""
Root URL configuration for HealthPortal.
Each app registers its own urls — this file just wires them together.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # App routes
    path("", include("dashboard.urls")),           # main frontend
    path("accounts/", include("accounts.urls")),   # auth
    path("appointments/", include("appointments.urls")),
    path("records/", include("records.urls")),

    # API routes — all under /api/v1/
    path("api/v1/", include("accounts.api_urls")),
    path("api/v1/", include("patients.api_urls")),
    path("api/v1/", include("doctors.api_urls")),
    path("api/v1/", include("appointments.api_urls")),
    path("api/v1/", include("records.api_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
