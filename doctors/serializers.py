"""
Serializers for the doctors app.
"""

from rest_framework import serializers
from .models import DoctorProfile, DoctorSchedule


class DoctorScheduleSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model  = DoctorSchedule
        fields = ("id", "day_of_week", "day_display", "start_time", "end_time", "slot_duration_minutes", "is_active")


class DoctorProfileSerializer(serializers.ModelSerializer):

    full_name      = serializers.CharField(source="user.get_full_name", read_only=True)
    email          = serializers.EmailField(source="user.email",        read_only=True)
    user_id        = serializers.IntegerField(source="user.id",         read_only=True)
    specialization_display = serializers.CharField(source="get_specialization_display", read_only=True)
    schedules      = DoctorScheduleSerializer(many=True, read_only=True)

    class Meta:
        model  = DoctorProfile
        fields = (
            "id", "user_id", "full_name", "email",
            "specialization", "specialization_display",
            "license_number", "bio", "years_of_exp",
            "consultation_fee", "is_available", "schedules",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "user_id", "full_name", "email", "created_at", "updated_at")
