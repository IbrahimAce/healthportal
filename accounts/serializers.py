"""
Serializers for auth flows — registration and user profile.
Validation is enforced here so views stay clean.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    """Used for patient self-registration. Doctors are created by admin."""

    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ("email", "first_name", "last_name", "phone", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        # Self-registered users are always patients
        return User.objects.create_user(role=Role.PATIENT, **validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only profile info returned after login or on /me/ endpoint."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model  = User
        fields = ("id", "email", "full_name", "first_name", "last_name", "phone", "role", "date_joined")
        read_only_fields = fields
