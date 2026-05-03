from django.urls import path
from .views import (
    patient_dashboard, doctor_dashboard,
    receptionist_dashboard, admin_dashboard,
)

app_name = "dashboard"

urlpatterns = [
    path("",              patient_dashboard,      name="patient"),
    path("doctor/",       doctor_dashboard,       name="doctor"),
    path("receptionist/", receptionist_dashboard, name="receptionist"),
    path("admin-dashboard/",        admin_dashboard,        name="admin"),
]
