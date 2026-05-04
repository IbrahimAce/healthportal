"""
Slot generation utility with Redis caching.

Doctor availability for a given day is cached for 5 minutes —
this is the most frequently queried and rarely changing data.
Cache is invalidated automatically on expiry.
"""

import datetime
from django.core.cache import cache
from .models import Appointment


def generate_slots(doctor_profile, date):
    """
    Returns a list of available (start_time, end_time) tuples
    for a given doctor on a given date.

    Results are cached per doctor+date for 5 minutes to reduce
    database hits during peak booking periods.
    """

    cache_key = f"slots__{doctor_profile.pk}__{date.isoformat()}"
    cached    = cache.get(cache_key)

    if cached is not None:
        return cached

    # Find doctor's schedule for this weekday
    schedule = doctor_profile.schedules.filter(
        day_of_week=date.weekday(),
        is_active=True
    ).first()

    if not schedule:
        cache.set(cache_key, [], 60 * 5)
        return []

    # Generate all possible slots
    slots   = []
    current = datetime.datetime.combine(date, schedule.start_time)
    end     = datetime.datetime.combine(date, schedule.end_time)
    delta   = datetime.timedelta(minutes=schedule.slot_duration_minutes)

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

    now   = datetime.datetime.now().time()
    today = datetime.date.today()

    available = []
    for start, end_time in slots:
        if start in booked_times:
            continue
        if date == today and start <= now:
            continue
        available.append((start, end_time))

    # Cache for 5 minutes
    cache.set(cache_key, available, 60 * 5)

    return available
