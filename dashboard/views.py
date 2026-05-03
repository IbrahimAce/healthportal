"""
Dashboard views — one per role.
Each dashboard pulls only the data relevant to that role.
These are intentionally kept focused — no cross-role data leaks.
"""

import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.models import Role
from appointments.models import Appointment


def _role_guard(request, expected_role):
    """Redirect user if they don't have the expected role."""
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.user.role != expected_role and not request.user.is_admin_user:
        return redirect("accounts:login")
    return None


@login_required
def patient_dashboard(request):
    today  = timezone.localdate()
    upcoming = Appointment.objects.filter(
        patient=request.user,
        date__gte=today,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).select_related("doctor", "doctor__doctor_profile").order_by("date", "start_time")[:5]

    recent = Appointment.objects.filter(
        patient=request.user,
        status=Appointment.Status.COMPLETED
    ).select_related("doctor").order_by("-date")[:3]

    return render(request, "dashboard/patient.html", {
        "upcoming": upcoming,
        "recent":   recent,
    })


@login_required
def doctor_dashboard(request):
    guard = _role_guard(request, Role.DOCTOR)
    if guard:
        return guard

    today = timezone.localdate()
    todays_appointments = Appointment.objects.filter(
        doctor=request.user,
        date=today,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).select_related("patient", "patient__patient_profile").order_by("start_time")

    upcoming = Appointment.objects.filter(
        doctor=request.user,
        date__gt=today,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).select_related("patient").order_by("date", "start_time")[:5]

    return render(request, "dashboard/doctor.html", {
        "todays_appointments": todays_appointments,
        "upcoming":            upcoming,
        "today":               today,
    })


@login_required
def receptionist_dashboard(request):
    guard = _role_guard(request, Role.RECEPTIONIST)
    if guard:
        return guard

    today = timezone.localdate()
    todays_appointments = Appointment.objects.filter(
        date=today
    ).select_related("patient", "doctor").order_by("start_time")

    pending = Appointment.objects.filter(
        status=Appointment.Status.PENDING
    ).select_related("patient", "doctor").order_by("date", "start_time")[:10]

    return render(request, "dashboard/receptionist.html", {
        "todays_appointments": todays_appointments,
        "pending":             pending,
    })


@login_required
def admin_dashboard(request):
    guard = _role_guard(request, Role.ADMIN)
    if guard:
        return guard

    from accounts.models import User
    from doctors.models import DoctorProfile

    today = timezone.localdate()

    stats = {
        "total_patients":     User.objects.filter(role=Role.PATIENT).count(),
        "total_doctors":      User.objects.filter(role=Role.DOCTOR).count(),
        "todays_appointments":Appointment.objects.filter(date=today).count(),
        "pending_appointments":Appointment.objects.filter(status=Appointment.Status.PENDING).count(),
    }

    recent_appointments = Appointment.objects.select_related(
        "patient", "doctor"
    ).order_by("-created_at")[:10]

    return render(request, "dashboard/admin.html", {
        "stats":               stats,
        "recent_appointments": recent_appointments,
    })
