"""
Appointment API views.

Patients: create and list their own appointments, cancel.
Doctors:  list their appointments, update status and notes.
Staff:    full access.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsPatient, IsDoctor, IsDoctorOrReceptionist, IsAdminUser
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentStatusUpdateSerializer,
)


class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/v1/appointments/  — list appointments (filtered by role)
    POST /api/v1/appointments/  — create a new appointment (patients only)
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields   = ["status", "date", "appointment_type"]
    ordering_fields    = ["date", "start_time", "created_at"]
    search_fields      = ["patient__first_name", "doctor__first_name", "reason"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Appointment.objects.filter(
                patient=user
            ).select_related("doctor", "doctor__doctor_profile")

        elif user.is_doctor:
            return Appointment.objects.filter(
                doctor=user
            ).select_related("patient", "patient__patient_profile")

        # Staff see all
        return Appointment.objects.select_related("patient", "doctor").all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_patient:
            return Response(
                {"detail": "Only patients can book appointments via API."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class AppointmentDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/appointments/<id>/  — retrieve appointment detail
    PATCH /api/v1/appointments/<id>/  — update status or doctor notes
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return AppointmentStatusUpdateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Appointment.objects.filter(patient=user)
        if user.is_doctor:
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.all()


class CancelAppointmentAPIView(APIView):
    """
    POST /api/v1/appointments/<id>/cancel/
    Cancels a pending or confirmed appointment.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        can_cancel = (
            (user.is_patient and appointment.patient == user) or
            (user.is_doctor  and appointment.doctor  == user) or
            user.is_receptionist or user.is_admin_user
        )

        if not can_cancel:
            return Response({"detail": "Not authorised."}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            return Response(
                {"detail": "This appointment cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        return Response({"detail": "Appointment cancelled."}, status=status.HTTP_200_OK)
