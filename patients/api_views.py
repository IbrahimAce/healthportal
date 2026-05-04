"""
Patient API views.

Patients can view and update their own profile.
Doctors, receptionists, and admins can list and view all patients.
"""

from rest_framework import generics, permissions
from accounts.permissions import IsPatient, IsDoctorOrReceptionist, IsAdminUser
from .models import PatientProfile
from .serializers import PatientProfileSerializer


class PatientProfileListAPIView(generics.ListAPIView):
    """
    GET /api/v1/patients/
    Staff-only: list all patient profiles.
    """
    serializer_class   = PatientProfileSerializer
    permission_classes = [IsDoctorOrReceptionist | IsAdminUser]
    queryset           = PatientProfile.objects.select_related("user").all()

    # Filtering by name or NHIF number via ?search=
    search_fields  = ["user__first_name", "user__last_name", "user__email", "sha_nhif_number"]
    ordering_fields = ["user__last_name", "created_at"]


class PatientProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    GET    /api/v1/patients/<id>/  — retrieve a patient profile
    PATCH  /api/v1/patients/<id>/  — patient updates their own profile
    """
    serializer_class = PatientProfileSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsDoctorOrReceptionist() | IsAdminUser() | IsPatient()]
        return [IsPatient()]  # only patient can update their own profile

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            # Patients can only retrieve their own profile
            return PatientProfile.objects.filter(user=user)
        return PatientProfile.objects.select_related("user").all()


class MyPatientProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/patients/me/
    PATCH /api/v1/patients/me/
    Convenience endpoint — patient gets/updates their own profile without knowing the ID.
    """
    serializer_class   = PatientProfileSerializer
    permission_classes = [IsPatient]

    def get_object(self):
        return PatientProfile.objects.get(user=self.request.user)
