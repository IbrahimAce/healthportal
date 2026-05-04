"""
Records API views — medical records, prescriptions, lab results.
"""

from rest_framework import generics, permissions
from accounts.permissions import IsDoctor, IsPatient, IsDoctorOrReceptionist
from .models import MedicalRecord, Prescription, LabResult
from .serializers import MedicalRecordSerializer, PrescriptionSerializer, LabResultSerializer


class MedicalRecordListAPIView(generics.ListAPIView):
    """
    GET /api/v1/records/
    Patients see their own. Doctors see records they wrote.
    """
    serializer_class   = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields    = ["created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return MedicalRecord.objects.filter(
                patient=user
            ).prefetch_related("prescriptions").select_related("doctor")
        if user.is_doctor:
            return MedicalRecord.objects.filter(
                doctor=user
            ).prefetch_related("prescriptions").select_related("patient")
        return MedicalRecord.objects.prefetch_related("prescriptions").select_related("patient", "doctor").all()


class MedicalRecordDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/v1/records/<id>/
    """
    serializer_class   = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return MedicalRecord.objects.filter(patient=user)
        if user.is_doctor:
            return MedicalRecord.objects.filter(doctor=user)
        return MedicalRecord.objects.all()


class PrescriptionListAPIView(generics.ListAPIView):
    """
    GET /api/v1/records/<record_id>/prescriptions/
    """
    serializer_class   = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.filter(
            medical_record_id=self.kwargs["record_pk"]
        )


class LabResultListAPIView(generics.ListAPIView):
    """
    GET /api/v1/labs/
    """
    serializer_class   = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields    = ["created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return LabResult.objects.filter(patient=user).select_related("appointment")
        return LabResult.objects.select_related("patient", "appointment").all()
