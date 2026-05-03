"""
Medical records, prescriptions, and lab results.

All three are linked to an Appointment — a record only exists
because a consultation happened. Doctors write, patients read.
"""

from django.db import models
from django.conf import settings


class MedicalRecord(models.Model):
    """
    Summary of a consultation written by the doctor.
    One record per completed appointment.
    """

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="medical_record",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="written_records",
        limit_choices_to={"role": "DOCTOR"},
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_records",
        limit_choices_to={"role": "PATIENT"},
    )

    diagnosis    = models.TextField()
    symptoms     = models.TextField(blank=True)
    treatment    = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes        = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record: {self.patient.get_full_name()} — {self.created_at.date()}"


class Prescription(models.Model):
    """
    Medication prescribed by a doctor after a consultation.
    Multiple prescriptions can exist per medical record.
    """

    FREQUENCY_CHOICES = [
        ("OD",  "Once Daily"),
        ("BD",  "Twice Daily"),
        ("TDS", "Three Times Daily"),
        ("QID", "Four Times Daily"),
        ("PRN", "As Needed"),
        ("STAT","Immediately / Once"),
    ]

    medical_record   = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name="prescriptions")
    medication_name  = models.CharField(max_length=200)
    dosage           = models.CharField(max_length=100, help_text="e.g. 500mg")
    frequency        = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    duration_days    = models.PositiveIntegerField(help_text="Number of days")
    instructions     = models.TextField(blank=True, help_text="e.g. Take after meals")
    is_active        = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication_name} {self.dosage} — {self.get_frequency_display()}"


class LabResult(models.Model):
    """
    Lab test result uploaded by a doctor or receptionist.
    Patients can view their own results.
    """

    STATUS_CHOICES = [
        ("PENDING",  "Pending"),
        ("READY",    "Ready"),
        ("REVIEWED", "Reviewed by Doctor"),
    ]

    appointment  = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="lab_results",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lab_results",
        limit_choices_to={"role": "PATIENT"},
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_lab_results",
    )

    test_name   = models.CharField(max_length=200)
    result_file = models.FileField(upload_to="lab_results/%Y/%m/")
    notes       = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} — {self.patient.get_full_name()} ({self.status})"
