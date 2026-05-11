"""
Slot generation utility - NO REDIS version for production
"""

import datetime
from .models import Appointment


def generate_slots(doctor_profile, date):
    """
    Returns a list of available (start_time, end_time) tuples
    for a given doctor on a given date.
    """
    
    # Find doctor's schedule for this weekday
    schedule = doctor_profile.schedules.filter(
        day_of_week=date.weekday(),
        is_active=True
    ).first()

    if not schedule:
        return []

    # Generate all possible slots
    slots = []
    current = datetime.datetime.combine(date, schedule.start_time)
    end = datetime.datetime.combine(date, schedule.end_time)
    delta = datetime.timedelta(minutes=schedule.slot_duration_minutes)

    while current + delta <= end:
        slots.append((current.time(), (current + delta).time()))
        current += delta

    # Remove already-booked slots
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor_profile.user,
            date=date,
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ]
        ).values_list("start_time", flat=True)
    )

    now = datetime.datetime.now().time()
    today = datetime.date.today()

    available = []
    for start, end_time in slots:
        if start in booked_times:
            continue
        if date == today and start <= now:
            continue
        available.append((start, end_time))

    return available
