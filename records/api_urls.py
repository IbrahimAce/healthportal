from django.urls import path
from .api_views import (
    MedicalRecordListAPIView,
    MedicalRecordDetailAPIView,
    PrescriptionListAPIView,
    LabResultListAPIView,
)

urlpatterns = [
    path("records/",                              MedicalRecordListAPIView.as_view(),   name="api-record-list"),
    path("records/<int:pk>/",                     MedicalRecordDetailAPIView.as_view(), name="api-record-detail"),
    path("records/<int:record_pk>/prescriptions/",PrescriptionListAPIView.as_view(),    name="api-prescription-list"),
    path("labs/",                                 LabResultListAPIView.as_view(),       name="api-lab-list"),
]
