"""
Appointment model — the heart of the portal.

Flow:
  Patient books → PENDING
  Receptionist/Doctor confirms → CONFIRMED
  Doctor completes the visit → COMPLETED
  Either party cancels → CANCELLED
  Patient no-shows → NO_SHOW
"""

from django.db import models
from django.conf import settings


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING   = "PENDING",    "Pending"
        CONFIRMED = "CONFIRMED",  "Confirmed"
        COMPLETED = "COMPLETED",  "Completed"
        CANCELLED = "CANCELLED",  "Cancelled"
        NO_SHOW   = "NO_SHOW",    "No Show"

    class AppointmentType(models.TextChoices):
        IN_PERSON = "IN_PERSON", "In Person"
        TELECONSULT = "TELECONSULT", "Teleconsultation"

    # Core relationships
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_patient",
        limit_choices_to={"role": "PATIENT"},
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_doctor",
        limit_choices_to={"role": "DOCTOR"},
    )

    # Scheduling
    date             = models.DateField()
    start_time       = models.TimeField()
    end_time         = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=AppointmentType.choices, default=AppointmentType.IN_PERSON)

    # Status tracking
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Patient notes (reason for visit)
    reason = models.TextField(blank=True, verbose_name="Reason for Visit")

    # Doctor notes (filled after consultation)
    doctor_notes = models.TextField(blank=True)

    # M-Pesa payment (Kenya-specific — mocked)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status   = models.CharField(
        max_length=20,
        choices=[("UNPAID","Unpaid"), ("PENDING","Pending"), ("PAID","Paid")],
        default="UNPAID"
    )
    mpesa_reference  = models.CharField(max_length=50, blank=True, verbose_name="M-Pesa Reference")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        # Prevent double-booking — one patient per slot per doctor
        unique_together = ("doctor", "date", "start_time")

    def __str__(self):
        return f"{self.patient.get_full_name()} → Dr. {self.doctor.get_full_name()} on {self.date} at {self.start_time}"

    @property
    def is_upcoming(self):
        from django.utils import timezone
        import datetime
        now = timezone.localdate()
        return self.date >= now and self.status in [self.Status.PENDING, self.Status.CONFIRMED]
