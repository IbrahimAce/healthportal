from django.urls import path
from .views_web import (
    book_appointment, load_slots, confirm_booking,
    appointment_list, appointment_detail, cancel_appointment,
)

app_name = "appointments"

urlpatterns = [
    path("",                 appointment_list,   name="list"),
    path("book/",            book_appointment,   name="book"),
    path("book/slots/",      load_slots,         name="slots"),       # HTMX endpoint
    path("book/confirm/",    confirm_booking,    name="confirm"),
    path("<int:pk>/",        appointment_detail, name="detail"),
    path("<int:pk>/cancel/", cancel_appointment, name="cancel"),
]
