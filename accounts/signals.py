"""
Signals that fire after a User is created.
Automatically creates the matching profile (PatientProfile or DoctorProfile)
so views never have to worry about a missing profile.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Runs every time a User is saved.
    On first creation, we spin up the right profile model.
    We import inside the function to avoid circular imports.
    """
    if not created:
        return

    if instance.role == Role.PATIENT:
        from patients.models import PatientProfile
        PatientProfile.objects.get_or_create(user=instance)

    elif instance.role == Role.DOCTOR:
        from doctors.models import DoctorProfile
        DoctorProfile.objects.get_or_create(user=instance)
