"""
Slot generation utility.

Given a doctor's schedule for a day, generates all possible time slots.
Then filters out already-booked ones so only free slots are shown.

This is pure Python logic — no Django views here — keeping concerns separate.
"""

import datetime
from .models import Appointment


def generate_slots(doctor_profile, date):
    """
    Returns a list of available (start_time, end_time) tuples
    for a given doctor on a given date.

    Steps:
      1. Find the doctor's schedule for that weekday
      2. Generate all slots within working hours
      3. Remove already-booked slots
      4. Remove slots in the past (if today)
    """

    # date.weekday() returns 0=Monday ... 6=Sunday — matches our DoctorSchedule.day_of_week
    schedule = doctor_profile.schedules.filter(
        day_of_week=date.weekday(),
        is_active=True
    ).first()

    if not schedule:
        return []  # doctor doesn't work this day

    slots = []
    current = datetime.datetime.combine(date, schedule.start_time)
    end     = datetime.datetime.combine(date, schedule.end_time)
    delta   = datetime.timedelta(minutes=schedule.slot_duration_minutes)

    while current + delta <= end:
        slots.append((current.time(), (current + delta).time()))
        current += delta

    # Fetch already booked start times for this doctor on this date
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

    # Filter out booked and past slots
    now = datetime.datetime.now().time()
    today = datetime.date.today()

    available = []
    for start, end_time in slots:
        if start in booked_times:
            continue
        # If booking for today, skip slots already passed
        if date == today and start <= now:
            continue
        available.append((start, end_time))

    return available
