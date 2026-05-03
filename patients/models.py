"""
PatientProfile — extended info for users with role=PATIENT.
Linked 1-to-1 with accounts.User. Created automatically via signal.
"""

from django.db import models
from django.conf import settings


class PatientProfile(models.Model):

    BLOOD_GROUPS = [
        ("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),
        ("AB+","AB+"),("AB-","AB-"),("O+","O+"),("O-","O-"),
    ]

    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
    date_of_birth= models.DateField(null=True, blank=True)
    gender       = models.CharField(max_length=10, choices=[("M","Male"),("F","Female"),("O","Other")], blank=True)
    blood_group  = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    address      = models.TextField(blank=True)

    # Kenya-specific: national health insurance number
    sha_nhif_number = models.CharField(max_length=30, blank=True, verbose_name="SHA/NHIF Number")

    # Emergency contact
    emergency_contact_name  = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"
