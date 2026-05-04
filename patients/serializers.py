"""
Serializers for the patients app.
PatientProfileSerializer exposes profile data alongside user info.
"""

from rest_framework import serializers
from .models import PatientProfile


class PatientProfileSerializer(serializers.ModelSerializer):

    # Flatten useful user fields into the profile response
    email      = serializers.EmailField(source="user.email",          read_only=True)
    full_name  = serializers.CharField(source="user.get_full_name",   read_only=True)
    phone      = serializers.CharField(source="user.phone",           read_only=True)
    user_id    = serializers.IntegerField(source="user.id",           read_only=True)

    class Meta:
        model  = PatientProfile
        fields = (
            "id", "user_id", "full_name", "email", "phone",
            "date_of_birth", "gender", "blood_group", "address",
            "sha_nhif_number",
            "emergency_contact_name", "emergency_contact_phone",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "user_id", "full_name", "email", "phone", "created_at", "updated_at")
