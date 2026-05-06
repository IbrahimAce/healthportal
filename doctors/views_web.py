"""
Web views for doctor schedule management.
Doctors can set their available days and hours from the dashboard.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DoctorProfile, DoctorSchedule


@login_required
def manage_schedule(request):
    """
    Doctor selects which days they are available and sets hours per day.
    Multiple days can be selected at once via checkboxes.
    """
    if not request.user.is_doctor:
        messages.error(request, "Only doctors can manage schedules.")
        return redirect("dashboard:patient")

    doctor_profile = request.user.doctor_profile

    if request.method == "POST":
        # Delete existing schedules and rebuild from form data
        doctor_profile.schedules.all().delete()

        days_selected = request.POST.getlist("days")  # list of day numbers e.g. ['0','1','3']

        for day in days_selected:
            start_key = f"start_time_{day}"
            end_key   = f"end_time_{day}"
            slot_key  = f"slot_duration_{day}"

            start = request.POST.get(start_key)
            end   = request.POST.get(end_key)
            slot  = request.POST.get(slot_key, "30")

            if start and end:
                DoctorSchedule.objects.create(
                    doctor               = doctor_profile,
                    day_of_week          = int(day),
                    start_time           = start,
                    end_time             = end,
                    slot_duration_minutes= int(slot),
                    is_active            = True,
                )

        messages.success(request, "Schedule updated successfully.")
        return redirect("doctors:schedule")

    # Build current schedule as a dict keyed by day number for template
    current_schedules = {s.day_of_week: s for s in doctor_profile.schedules.all()}

    days = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    return render(request, "doctors/schedule.html", {
        "days":             days,
        "current_schedules":current_schedules,
    })
