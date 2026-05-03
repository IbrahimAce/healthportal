"""
Custom User model for HealthPortal.
We extend AbstractBaseUser so we have full control over auth fields.
Roles determine what each user can see and do across the system.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    PATIENT      = "PATIENT",      "Patient"
    DOCTOR       = "DOCTOR",       "Doctor"
    RECEPTIONIST = "RECEPTIONIST", "Receptionist"
    ADMIN        = "ADMIN",        "Admin"


class UserManager(BaseUserManager):
    """Custom manager — we use email as the unique identifier, not username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user model. One account per person regardless of role.
    Profile details (e.g. doctor bio, patient NHIF number) live in
    separate models linked via OneToOneField.
    """

    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone      = models.CharField(max_length=20, blank=True)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # --- Role helpers (used in views and templates) ---
    @property
    def is_patient(self):
        return self.role == Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == Role.DOCTOR

    @property
    def is_receptionist(self):
        return self.role == Role.RECEPTIONIST

    @property
    def is_admin_user(self):
        return self.role == Role.ADMIN
