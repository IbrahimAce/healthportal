from django.urls import path
from .api_views import (
    AppointmentListCreateAPIView,
    AppointmentDetailAPIView,
    CancelAppointmentAPIView,
)

urlpatterns = [
    path("appointments/",               AppointmentListCreateAPIView.as_view(), name="api-appointment-list"),
    path("appointments/<int:pk>/",      AppointmentDetailAPIView.as_view(),     name="api-appointment-detail"),
    path("appointments/<int:pk>/cancel/",CancelAppointmentAPIView.as_view(),    name="api-appointment-cancel"),
]
