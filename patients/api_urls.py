from django.urls import path
from .api_views import PatientProfileListAPIView, PatientProfileDetailAPIView, MyPatientProfileAPIView

urlpatterns = [
    path("patients/",         PatientProfileListAPIView.as_view(),   name="api-patient-list"),
    path("patients/me/",      MyPatientProfileAPIView.as_view(),     name="api-patient-me"),
    path("patients/<int:pk>/",PatientProfileDetailAPIView.as_view(), name="api-patient-detail"),
]
