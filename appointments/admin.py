"""
Admin config for Appointment.
Staff can search, filter by status, and update appointments here.
"""

from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ("patient", "doctor", "date", "start_time", "status", "payment_status", "appointment_type")
    list_filter   = ("status", "appointment_type", "payment_status", "date")
    search_fields = (
        "patient__first_name", "patient__last_name",
        "doctor__first_name",  "doctor__last_name",
        "mpesa_reference",
    )
    readonly_fields  = ("created_at", "updated_at")
    date_hierarchy   = "date"
    ordering         = ("-date", "-start_time")

    # Allow quick status update directly from the list view
    list_editable = ("status", "payment_status")
