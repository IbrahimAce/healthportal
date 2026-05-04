"""
Serializers for medical records, prescriptions, and lab results.
"""

from rest_framework import serializers
from .models import MedicalRecord, Prescription, LabResult


class PrescriptionSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)

    class Meta:
        model  = Prescription
        fields = (
            "id", "medication_name", "dosage",
            "frequency", "frequency_display",
            "duration_days", "instructions", "is_active", "created_at",
        )
        read_only_fields = ("id", "frequency_display", "created_at")


class MedicalRecordSerializer(serializers.ModelSerializer):
    prescriptions  = PrescriptionSerializer(many=True, read_only=True)
    patient_name   = serializers.CharField(source="patient.get_full_name", read_only=True)
    doctor_name    = serializers.CharField(source="doctor.get_full_name",  read_only=True)

    class Meta:
        model  = MedicalRecord
        fields = (
            "id", "appointment",
            "patient", "patient_name",
            "doctor",  "doctor_name",
            "diagnosis", "symptoms", "treatment", "notes",
            "follow_up_date", "prescriptions",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "patient_name", "doctor_name", "prescriptions", "created_at", "updated_at")


class LabResultSerializer(serializers.ModelSerializer):
    patient_name    = serializers.CharField(source="patient.get_full_name",    read_only=True)
    uploaded_by_name= serializers.CharField(source="uploaded_by.get_full_name",read_only=True)
    status_display  = serializers.CharField(source="get_status_display",       read_only=True)
    file_url        = serializers.SerializerMethodField()

    class Meta:
        model  = LabResult
        fields = (
            "id", "appointment",
            "patient", "patient_name",
            "uploaded_by", "uploaded_by_name",
            "test_name", "notes",
            "status", "status_display",
            "file_url",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "patient_name", "uploaded_by_name", "status_display", "file_url", "created_at", "updated_at")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.result_file and request:
            return request.build_absolute_uri(obj.result_file.url)
        return None
