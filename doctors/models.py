"""
DoctorProfile — extended info for users with role=DOCTOR.
DoctorSchedule — defines which days and times a doctor is available.
Both are linked to accounts.User via OneToOneField / ForeignKey.
"""

from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):

    SPECIALIZATIONS = [
        ("GP",          "General Practitioner"),
        ("PEDIATRICS",  "Pediatrics"),
        ("SURGERY",     "Surgery"),
        ("GYNECOLOGY",  "Gynecology"),
        ("CARDIOLOGY",  "Cardiology"),
        ("ORTHOPEDICS", "Orthopedics"),
        ("PSYCHIATRY",  "Psychiatry"),
        ("DERMATOLOGY", "Dermatology"),
        ("OTHER",       "Other"),
    ]

    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialization   = models.CharField(max_length=50, choices=SPECIALIZATIONS, default="GP")
    license_number   = models.CharField(max_length=50, blank=True)
    bio              = models.TextField(blank=True)
    years_of_exp     = models.PositiveIntegerField(default=0, verbose_name="Years of Experience")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available     = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialization_display()})"


class DoctorSchedule(models.Model):
    """
    Defines a doctor's weekly availability.
    One row per working day — e.g. Monday 08:00–17:00.
    Appointment slots are generated from these rows.
    """

    DAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    doctor     = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="schedules")
    day_of_week= models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time   = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(default=30, help_text="Length of each appointment slot in minutes")
    is_active  = models.BooleanField(default=True)

    class Meta:
        unique_together = ("doctor", "day_of_week")
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.doctor} — {self.get_day_of_week_display()} {self.start_time}–{self.end_time}"
