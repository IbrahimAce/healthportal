"""
Records views — medical records, prescriptions, lab results.

Access rules:
  - Doctors write records and prescriptions for their own patients
  - Patients read their own records only
  - Lab results can be uploaded by doctors or receptionists
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from appointments.models import Appointment
from .models import MedicalRecord, Prescription, LabResult


# ---------------------------------------------------------------------------
# Medical Records
# ---------------------------------------------------------------------------

@login_required
def record_list(request):
    """
    Patients see their own records.
    Doctors see records they wrote.
    """
    user = request.user

    if user.is_patient:
        records = MedicalRecord.objects.filter(
            patient=user
        ).select_related("doctor", "appointment").order_by("-created_at")

    elif user.is_doctor:
        records = MedicalRecord.objects.filter(
            doctor=user
        ).select_related("patient", "appointment").order_by("-created_at")

    else:
        records = MedicalRecord.objects.all().select_related(
            "patient", "doctor"
        ).order_by("-created_at")

    return render(request, "records/record_list.html", {"records": records})


@login_required
def record_detail(request, pk):
    """
    Full view of a single medical record including prescriptions.
    """
    record = get_object_or_404(MedicalRecord, pk=pk)
    user   = request.user

    # Access control
    if user.is_patient and record.patient != user:
        messages.error(request, "You do not have access to this record.")
        return redirect("records:list")

    if user.is_doctor and record.doctor != user:
        messages.error(request, "You do not have access to this record.")
        return redirect("records:list")

    prescriptions = record.prescriptions.all()

    return render(request, "records/record_detail.html", {
        "record":        record,
        "prescriptions": prescriptions,
    })


@login_required
def write_record(request, appointment_pk):
    """
    Doctor writes a medical record for a completed appointment.
    Only the doctor assigned to the appointment can do this.
    """
    user        = request.user
    appointment = get_object_or_404(Appointment, pk=appointment_pk)

    if not user.is_doctor:
        messages.error(request, "Only doctors can write medical records.")
        return redirect("appointments:list")

    if appointment.doctor != user:
        messages.error(request, "You are not the assigned doctor for this appointment.")
        return redirect("appointments:list")

    # Prevent duplicate records
    if hasattr(appointment, "medical_record"):
        messages.info(request, "A record already exists for this appointment.")
        return redirect("records:detail", pk=appointment.medical_record.pk)

    if request.method == "POST":
        diagnosis      = request.POST.get("diagnosis", "").strip()
        symptoms       = request.POST.get("symptoms", "").strip()
        treatment      = request.POST.get("treatment", "").strip()
        notes          = request.POST.get("notes", "").strip()
        follow_up_date = request.POST.get("follow_up_date") or None

        if not diagnosis:
            messages.error(request, "Diagnosis is required.")
        else:
            record = MedicalRecord.objects.create(
                appointment    = appointment,
                doctor         = user,
                patient        = appointment.patient,
                diagnosis      = diagnosis,
                symptoms       = symptoms,
                treatment      = treatment,
                notes          = notes,
                follow_up_date = follow_up_date,
            )
            # Mark appointment as completed
            appointment.status = Appointment.Status.COMPLETED
            appointment.save()

            messages.success(request, "Medical record saved successfully.")
            return redirect("records:detail", pk=record.pk)

    return render(request, "records/write_record.html", {"appointment": appointment})


# ---------------------------------------------------------------------------
# Prescriptions
# ---------------------------------------------------------------------------

@login_required
def add_prescription(request, record_pk):
    """
    Doctor adds a prescription to an existing medical record.
    Uses HTMX — returns only the updated prescription list partial.
    """
    user   = request.user
    record = get_object_or_404(MedicalRecord, pk=record_pk)

    if not user.is_doctor or record.doctor != user:
        messages.error(request, "Not authorised.")
        return redirect("records:list")

    if request.method == "POST":
        medication_name = request.POST.get("medication_name", "").strip()
        dosage          = request.POST.get("dosage", "").strip()
        frequency       = request.POST.get("frequency", "")
        duration_days   = request.POST.get("duration_days", 1)
        instructions    = request.POST.get("instructions", "").strip()

        if medication_name and dosage and frequency:
            Prescription.objects.create(
                medical_record  = record,
                medication_name = medication_name,
                dosage          = dosage,
                frequency       = frequency,
                duration_days   = int(duration_days),
                instructions    = instructions,
            )

    # Return HTMX partial with updated list
    prescriptions = record.prescriptions.all()
    return render(request, "records/partials/prescription_list.html", {
        "prescriptions": prescriptions,
        "record":        record,
    })


# ---------------------------------------------------------------------------
# Lab Results
# ---------------------------------------------------------------------------

@login_required
def lab_result_list(request):
    """Patient sees their own lab results. Doctor/staff see all they uploaded."""
    user = request.user

    if user.is_patient:
        results = LabResult.objects.filter(
            patient=user
        ).select_related("appointment").order_by("-created_at")
    else:
        results = LabResult.objects.filter(
            uploaded_by=user
        ).select_related("patient", "appointment").order_by("-created_at")

    return render(request, "records/lab_list.html", {"results": results})


@login_required
def upload_lab_result(request, appointment_pk):
    """
    Doctor or receptionist uploads a lab result for a patient.
    """
    user        = request.user
    appointment = get_object_or_404(Appointment, pk=appointment_pk)

    if not (user.is_doctor or user.is_receptionist):
        messages.error(request, "Not authorised to upload lab results.")
        return redirect("appointments:list")

    if request.method == "POST":
        test_name   = request.POST.get("test_name", "").strip()
        notes       = request.POST.get("notes", "").strip()
        result_file = request.FILES.get("result_file")

        if not test_name or not result_file:
            messages.error(request, "Test name and file are required.")
        else:
            LabResult.objects.create(
                appointment = appointment,
                patient     = appointment.patient,
                uploaded_by = user,
                test_name   = test_name,
                notes       = notes,
                result_file = result_file,
            )
            messages.success(request, f"Lab result '{test_name}' uploaded successfully.")
            return redirect("appointments:detail", pk=appointment_pk)

    return render(request, "records/upload_lab.html", {"appointment": appointment})
