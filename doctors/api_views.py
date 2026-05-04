"""
Doctor API views.

Public: list available doctors (patients need to browse doctors to book).
Protected: retrieve/update individual doctor profile.
"""

from rest_framework import generics, permissions
from accounts.permissions import IsDoctor, IsAdminUser
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer


class DoctorProfileListAPIView(generics.ListAPIView):
    """
    GET /api/v1/doctors/
    Authenticated users can list available doctors.
    Used by the booking flow to show doctor options.
    """
    serializer_class   = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields      = ["user__first_name", "user__last_name", "specialization"]
    filterset_fields   = ["specialization", "is_available"]
    ordering_fields    = ["user__last_name", "consultation_fee", "years_of_exp"]

    def get_queryset(self):
        return DoctorProfile.objects.filter(
            is_available=True
        ).select_related("user").prefetch_related("schedules")


class DoctorProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/doctors/<id>/  — anyone authenticated can view a doctor profile
    PATCH /api/v1/doctors/<id>/  — only the doctor themselves or admin can update
    """
    serializer_class = DoctorProfileSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsDoctor() | IsAdminUser()]

    def get_queryset(self):
        return DoctorProfile.objects.select_related("user").prefetch_related("schedules").all()
