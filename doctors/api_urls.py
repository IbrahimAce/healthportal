from django.urls import path
from .api_views import DoctorProfileListAPIView, DoctorProfileDetailAPIView

urlpatterns = [
    path("doctors/",          DoctorProfileListAPIView.as_view(),   name="api-doctor-list"),
    path("doctors/<int:pk>/", DoctorProfileDetailAPIView.as_view(), name="api-doctor-detail"),
]
