"""
Web views for the appointment booking flow.

GET  /appointments/book/          — step 1: choose a doctor
GET  /appointments/book/slots/    — HTMX partial: load slots for chosen doctor + date
POST /appointments/book/confirm/  — step 2: confirm and save booking
GET  /appointments/                — patient's appointment list
GET  /appointments/<id>/          — appointment detail
POST /appointments/<id>/cancel/   — cancel an appointment
"""

import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from doctors.models import DoctorProfile
from accounts.models import User, Role
from .models import Appointment
from .slots import generate_slots

def _parse_date(date_str):
    """
    Normalize a date string to a datetime.date object.
    Handles all browser/locale formats including Firefox which sends
    spaces around slashes: '05 / 12 / 2026'
    Returns None if date_str is empty or None.
    """
    if not date_str:
        return None

    # Clean the string
    raw = date_str.replace(" ", "").strip()
    if not raw:
        return None

    # Remove any timezone info if present
    if 'T' in raw:
        raw = raw.split('T')[0]
    if '+' in raw:
        raw = raw.split('+')[0]

    # Try ISO format YYYY-MM-DD first (most common)
    try:
        return datetime.date.fromisoformat(raw)
    except ValueError:
        pass

    # Try DD/MM/YYYY format
    if "/" in raw:
        parts = raw.split("/")
        if len(parts) == 3:
            # Try YYYY/MM/DD
            if len(parts[0]) == 4:
                try:
                    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                except ValueError:
                    pass

            # Try MM/DD/YYYY or DD/MM/YYYY
            try:
                # Assume DD/MM/YYYY
                return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
            except (ValueError, IndexError):
                pass

    # Try parsing with datetime.strptime as fallback
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    return None

@login_required
def book_appointment(request):
    """
    Step 1 — patient picks a doctor and a date.
    The date defaults to tomorrow.
    """
    doctors = DoctorProfile.objects.filter(
        is_available=True
    ).select_related("user").prefetch_related("schedules")

    tomorrow = (timezone.localdate() + datetime.timedelta(days=1)).isoformat()

    return render(request, "appointments/book.html", {
        "doctors":  doctors,
        "tomorrow": tomorrow,
    })


@login_required
def load_slots(request):
    """
    HTMX endpoint — called when patient selects a doctor + date.
    Returns only the slots partial (no full page reload).
    """
    doctor_id = request.GET.get("doctor_id")
    date_str  = request.GET.get("date")

    slots  = []
    error  = None
    doctor = None

    if doctor_id and date_str:
        try:
            doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
            date   = _parse_date(date_str)

            # Debug print (remove after testing)
            print(f"DEBUG: date_str='{date_str}', parsed date={date}")

            if date is None:
                error = "Please select a valid date."
            elif date < timezone.localdate():
                error = "Please select a future date."
            else:
                # Ensure date is a date object, not string
                if isinstance(date, str):
                    date = _parse_date(date)
                slots = generate_slots(doctor, date)
                if not slots:
                    error = "No available slots for this doctor on the selected date."

        except Exception as e:
            print(f"ERROR in load_slots: {str(e)}")  # Debug
            error = f"Invalid date format. Please use YYYY-MM-DD."

    return render(request, "appointments/partials/slots.html", {
        "slots":  slots,
        "doctor": doctor,
        "date":   date_str,
        "error":  error,
    })


@login_required
def confirm_booking(request):
    """
    Step 2 — patient submits chosen slot.
    Creates the Appointment and redirects to their dashboard.
    """
    if request.method != "POST":
        return redirect("appointments:book")

    doctor_id = request.POST.get("doctor_id")
    date_str  = request.POST.get("date")
    start_str = request.POST.get("start_time")
    end_str   = request.POST.get("end_time")
    reason    = request.POST.get("reason", "")
    appt_type = request.POST.get("appointment_type", Appointment.AppointmentType.IN_PERSON)

    try:
        doctor = get_object_or_404(User, pk=doctor_id)
        if not doctor.is_doctor:
            messages.error(request, "Selected user is not a doctor.")
            return redirect("appointments:book")

        date = _parse_date(date_str)
        if date is None:
            messages.error(request, "Invalid date format. Please go back and select a date.")
            return redirect("appointments:book")

        # Handle time parsing with better error messages
        if not start_str or not end_str:
            messages.error(request, "Missing time slot. Please go back and select a time.")
            return redirect("appointments:book")

        try:
            start_time = datetime.time.fromisoformat(start_str)
            end_time = datetime.time.fromisoformat(end_str)
        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid time format: {start_str} or {end_str}. Please try again.")
            return redirect("appointments:book")

    except (ValueError, TypeError, User.DoesNotExist) as e:
        messages.error(request, f"Invalid booking data: {str(e)}. Please try again.")
        return redirect("appointments:book")

    if date is None:
        messages.error(request, "Invalid date. Please try again.")
        return redirect("appointments:book")

    # Guard against double booking at submit time
    if Appointment.objects.filter(
        doctor=doctor, date=date, start_time=start_time,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).exists():
        messages.error(request, "That slot was just taken. Please choose another.")
        return redirect("appointments:book")

    # Get doctor's consultation fee
    fee = 0
    if hasattr(doctor, "doctor_profile"):
        fee = doctor.doctor_profile.consultation_fee

    appointment = Appointment.objects.create(
        patient          = request.user,
        doctor           = doctor,
        date             = date,
        start_time       = start_time,
        end_time         = end_time,
        reason           = reason,
        appointment_type = appt_type,
        consultation_fee = fee,
        status           = Appointment.Status.PENDING,
    )

    # Fire notification tasks asynchronously — don't block the response
    from notifications.tasks import (
        send_appointment_confirmation_email,
        send_sms_reminder,
    )
    send_appointment_confirmation_email.delay(appointment.pk)
    send_sms_reminder.delay(appointment.pk)

    messages.success(request, f"Appointment booked for {date} at {start_time.strftime('%H:%M')}. Awaiting confirmation.")
    return redirect("appointments:detail", pk=appointment.pk)


@login_required
def appointment_list(request):
    """
    Patient sees their own appointments.
    Doctor sees appointments assigned to them.
    """
    user = request.user

    if user.is_patient:
        appointments = Appointment.objects.filter(
            patient=user
        ).select_related("doctor", "doctor__doctor_profile").order_by("-date", "-start_time")

    elif user.is_doctor:
        appointments = Appointment.objects.filter(
            doctor=user
        ).select_related("patient", "patient__patient_profile").order_by("-date", "-start_time")

    else:
        appointments = Appointment.objects.all().select_related(
            "patient", "doctor"
        ).order_by("-date", "-start_time")

    return render(request, "appointments/list.html", {"appointments": appointments})


@login_required
def appointment_detail(request, pk):
    """
    Shows full detail of one appointment.
    Access is restricted — only the patient, doctor, or staff can view.
    """
    appointment = get_object_or_404(Appointment, pk=pk)
    user        = request.user

    if user.is_patient and appointment.patient != user:
        messages.error(request, "You do not have access to this appointment.")
        return redirect("appointments:list")

    if user.is_doctor and appointment.doctor != user:
        messages.error(request, "You do not have access to this appointment.")
        return redirect("appointments:list")

    return render(request, "appointments/detail.html", {"appointment": appointment})


@login_required
def cancel_appointment(request, pk):
    """
    Patient or doctor can cancel a PENDING or CONFIRMED appointment.
    """
    appointment = get_object_or_404(Appointment, pk=pk)
    user        = request.user

    can_cancel = (
        (user.is_patient and appointment.patient == user) or
        (user.is_doctor  and appointment.doctor  == user) or
        user.is_receptionist or user.is_admin_user
    )

    if not can_cancel:
        messages.error(request, "You cannot cancel this appointment.")
        return redirect("appointments:list")

    if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
        messages.error(request, "This appointment cannot be cancelled.")
        return redirect("appointments:detail", pk=pk)

    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()

        from notifications.tasks import send_appointment_cancellation_email
        send_appointment_cancellation_email.delay(appointment.pk)

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("appointments:list")

    return render(request, "appointments/cancel_confirm.html", {"appointment": appointment})
