"""
Web (template) views for login, register, and logout.
These serve the HTMX-powered frontend — not the API.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Role


def login_view(request):
    """
    GET  — render login form
    POST — authenticate and redirect by role
    """
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == "POST":
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user     = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return _redirect_by_role(user)
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


def register_view(request):
    """
    Self-registration for patients only.
    Doctors and receptionists are created by admin.
    """
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == "POST":
        data = request.POST
        email     = data.get("email", "").strip().lower()
        first     = data.get("first_name", "").strip()
        last      = data.get("last_name", "").strip()
        phone     = data.get("phone", "").strip()
        password  = data.get("password", "")
        password2 = data.get("password2", "")

        # Basic server-side validation
        if password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
        else:
            user = User.objects.create_user(
                email=email, first_name=first, last_name=last,
                phone=phone, password=password, role=Role.PATIENT
            )
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account is ready.")
            return redirect("dashboard:patient")

    return render(request, "accounts/register.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _redirect_by_role(user):
    """Send users to the correct dashboard based on their role."""
    role_map = {
        Role.PATIENT:      "dashboard:patient",
        Role.DOCTOR:       "dashboard:doctor",
        Role.RECEPTIONIST: "dashboard:receptionist",
        Role.ADMIN:        "dashboard:admin",
    }
    return redirect(role_map.get(user.role, "dashboard:patient"))
