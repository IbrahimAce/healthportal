"""
Admin config for DoctorProfile and DoctorSchedule.
"""

from django.contrib import admin
from .models import DoctorProfile, DoctorSchedule


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display  = ("get_full_name", "specialization", "license_number", "consultation_fee", "is_available")
    search_fields = ("user__email", "user__first_name", "user__last_name", "license_number")
    list_filter   = ("specialization", "is_available")
    readonly_fields = ("created_at", "updated_at")

    def get_full_name(self, obj):
        return f"Dr. {obj.user.get_full_name()}"
    get_full_name.short_description = "Doctor"


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display  = ("doctor", "get_day_of_week_display", "start_time", "end_time", "is_active")
    list_filter   = ("day_of_week", "is_active")
    search_fields = ("doctor__user__first_name", "doctor__user__last_name")
