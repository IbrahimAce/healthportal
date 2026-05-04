"""
Serializers for the appointments app.
"""

from rest_framework import serializers
from accounts.serializers import UserProfileSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    patient_detail = UserProfileSerializer(source="patient", read_only=True)
    doctor_detail  = UserProfileSerializer(source="doctor",  read_only=True)
    status_display          = serializers.CharField(source="get_status_display",          read_only=True)
    appointment_type_display= serializers.CharField(source="get_appointment_type_display",read_only=True)

    class Meta:
        model  = Appointment
        fields = (
            "id",
            "patient", "patient_detail",
            "doctor",  "doctor_detail",
            "date", "start_time", "end_time",
            "appointment_type", "appointment_type_display",
            "status", "status_display",
            "reason", "doctor_notes",
            "consultation_fee", "payment_status", "mpesa_reference",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "patient_detail", "doctor_detail",
            "status_display", "appointment_type_display",
            "created_at", "updated_at",
        )


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Used for POST /api/v1/appointments/
    Patient is set automatically from the request — not accepted from payload.
    """

    class Meta:
        model  = Appointment
        fields = ("doctor", "date", "start_time", "end_time", "appointment_type", "reason")

    def validate(self, attrs):
        # Prevent double booking at serializer level
        if Appointment.objects.filter(
            doctor     = attrs["doctor"],
            date       = attrs["date"],
            start_time = attrs["start_time"],
            status__in = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        ).exists():
            raise serializers.ValidationError("This slot is already booked.")
        return attrs

    def create(self, validated_data):
        # Inject the patient from the request context
        validated_data["patient"] = self.context["request"].user
        fee = 0
        doctor = validated_data.get("doctor")
        if hasattr(doctor, "doctor_profile"):
            fee = doctor.doctor_profile.consultation_fee
        validated_data["consultation_fee"] = fee
        return super().create(validated_data)


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Used for PATCH — only status and doctor_notes can be updated this way.
    """

    class Meta:
        model  = Appointment
        fields = ("status", "doctor_notes")
