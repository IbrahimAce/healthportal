"""
Admin config for PatientProfile.
Receptionists and admins use this to manage patient records.
"""

from django.contrib import admin
from .models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display  = ("get_full_name", "gender", "blood_group", "sha_nhif_number", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "sha_nhif_number")
    list_filter   = ("gender", "blood_group")
    readonly_fields = ("created_at", "updated_at")

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Patient Name"
