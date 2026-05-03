"""
DoctorProfile — extended info for users with role=DOCTOR.
Linked 1-to-1 with accounts.User. Created automatically via signal.
"""

from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):

    SPECIALIZATIONS = [
        ("GP",         "General Practitioner"),
        ("PEDIATRICS", "Pediatrics"),
        ("SURGERY",    "Surgery"),
        ("GYNECOLOGY", "Gynecology"),
        ("CARDIOLOGY", "Cardiology"),
        ("ORTHOPEDICS","Orthopedics"),
        ("PSYCHIATRY", "Psychiatry"),
        ("DERMATOLOGY","Dermatology"),
        ("OTHER",      "Other"),
    ]

    user           = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS, default="GP")
    license_number = models.CharField(max_length=50, blank=True)
    bio            = models.TextField(blank=True)
    years_of_exp   = models.PositiveIntegerField(default=0, verbose_name="Years of Experience")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available   = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialization_display()})"
