"""
Admin config for MedicalRecord, Prescription, and LabResult.
"""

from django.contrib import admin
from .models import MedicalRecord, Prescription, LabResult


class PrescriptionInline(admin.TabularInline):
    """Show prescriptions directly inside the MedicalRecord detail page."""
    model  = Prescription
    extra  = 1
    fields = ("medication_name", "dosage", "frequency", "duration_days", "instructions", "is_active")


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display  = ("patient", "doctor", "created_at", "follow_up_date")
    search_fields = ("patient__first_name", "patient__last_name", "diagnosis")
    list_filter   = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines       = [PrescriptionInline]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ("medication_name", "dosage", "frequency", "duration_days", "is_active")
    list_filter   = ("frequency", "is_active")
    search_fields = ("medication_name",)


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display  = ("test_name", "patient", "status", "created_at")
    list_filter   = ("status",)
    search_fields = ("test_name", "patient__first_name", "patient__last_name")
    readonly_fields = ("created_at", "updated_at")
