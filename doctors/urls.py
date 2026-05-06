from django.urls import path
from .views_web import manage_schedule

app_name = "doctors"

urlpatterns = [
    path("schedule/", manage_schedule, name="schedule"),
]
