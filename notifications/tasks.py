"""
Celery tasks for HealthPortal notifications.

All external calls (email, SMS) are wrapped in try/except so a
failed notification never breaks the main booking flow.

SMS via Africa's Talking is mocked — the task logs what would be
sent instead of calling the real API. Swap in the real SDK later.
"""

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email tasks
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_confirmation_email(self, appointment_id):
    """
    Sends a confirmation email to the patient when an appointment
    is booked. Retries up to 3 times on failure (60s apart).
    """
    try:
        from appointments.models import Appointment
        appt = Appointment.objects.select_related("patient", "doctor").get(pk=appointment_id)

        subject = f"Appointment Confirmed — {appt.date} at {appt.start_time.strftime('%H:%M')}"
        message = (
            f"Dear {appt.patient.get_full_name()},\n\n"
            f"Your appointment has been booked successfully.\n\n"
            f"Doctor : Dr. {appt.doctor.get_full_name()}\n"
            f"Date   : {appt.date}\n"
            f"Time   : {appt.start_time.strftime('%H:%M')} – {appt.end_time.strftime('%H:%M')}\n"
            f"Type   : {appt.get_appointment_type_display()}\n\n"
            f"Please arrive 10 minutes early.\n\n"
            f"— {settings.SITE_NAME}"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [appt.patient.email])
        logger.info(f"Confirmation email sent to {appt.patient.email} for appointment {appointment_id}")

    except Exception as exc:
        logger.error(f"Failed to send confirmation email for appointment {appointment_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_cancellation_email(self, appointment_id):
    """
    Notifies patient and doctor when an appointment is cancelled.
    """
    try:
        from appointments.models import Appointment
        appt = Appointment.objects.select_related("patient", "doctor").get(pk=appointment_id)

        subject = f"Appointment Cancelled — {appt.date} at {appt.start_time.strftime('%H:%M')}"
        message = (
            f"Dear {appt.patient.get_full_name()},\n\n"
            f"Your appointment with Dr. {appt.doctor.get_full_name()} "
            f"on {appt.date} at {appt.start_time.strftime('%H:%M')} has been cancelled.\n\n"
            f"Please visit the portal to book a new appointment.\n\n"
            f"— {settings.SITE_NAME}"
        )

        recipients = [appt.patient.email, appt.doctor.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
        logger.info(f"Cancellation email sent for appointment {appointment_id}")

    except Exception as exc:
        logger.error(f"Failed to send cancellation email for appointment {appointment_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_reminder_email(self, appointment_id):
    """
    24-hour reminder email. Scheduled via Celery beat or
    triggered manually — called after booking confirmation.
    """
    try:
        from appointments.models import Appointment
        appt = Appointment.objects.select_related("patient", "doctor").get(pk=appointment_id)

        if appt.status not in ["PENDING", "CONFIRMED"]:
            logger.info(f"Reminder skipped — appointment {appointment_id} status is {appt.status}")
            return

        subject = f"Reminder: Appointment Tomorrow — {appt.date} at {appt.start_time.strftime('%H:%M')}"
        message = (
            f"Dear {appt.patient.get_full_name()},\n\n"
            f"This is a reminder that you have an appointment tomorrow.\n\n"
            f"Doctor : Dr. {appt.doctor.get_full_name()}\n"
            f"Date   : {appt.date}\n"
            f"Time   : {appt.start_time.strftime('%H:%M')}\n\n"
            f"— {settings.SITE_NAME}"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [appt.patient.email])
        logger.info(f"Reminder email sent to {appt.patient.email} for appointment {appointment_id}")

    except Exception as exc:
        logger.error(f"Failed to send reminder for appointment {appointment_id}: {exc}")
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# SMS task (Africa's Talking — mocked)
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_sms_reminder(self, appointment_id):
    """
    Sends an SMS reminder to the patient via Africa's Talking.

    MOCKED: logs the message instead of calling the real API.
    To go live, install africas-talking SDK and replace the
    logger.info call with the real send() call.

    Worldwide equivalent: Twilio in the US/EU,
    Africa's Talking is the standard in Kenya/East Africa.
    """
    try:
        from appointments.models import Appointment
        appt = Appointment.objects.select_related("patient").get(pk=appointment_id)

        phone   = appt.patient.phone
        message = (
            f"[{settings.SITE_NAME}] Reminder: Appointment with "
            f"Dr. {appt.doctor.get_full_name()} on {appt.date} "
            f"at {appt.start_time.strftime('%H:%M')}. Reply CANCEL to cancel."
        )

        # --- MOCK: replace below with real Africa's Talking call ---
        # import africastalking
        # africastalking.initialize(username, api_key)
        # sms = africastalking.SMS
        # sms.send(message, [phone])
        # -----------------------------------------------------------

        logger.info(f"[MOCK SMS] To: {phone} | Message: {message}")

    except Exception as exc:
        logger.error(f"SMS task failed for appointment {appointment_id}: {exc}")
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# M-Pesa payment task (mocked)
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_mpesa_payment(self, appointment_id, phone_number):
    """
    Initiates an M-Pesa STK push for the consultation fee.

    MOCKED: simulates the Daraja API call by marking the
    appointment payment as PENDING and logging the request.

    Worldwide equivalent: Stripe in US/EU, M-Pesa via Daraja
    API is the standard payment method in Kenya.
    """
    try:
        from appointments.models import Appointment
        appt = Appointment.objects.get(pk=appointment_id)

        # --- MOCK: replace with real Daraja STK push call ---
        # daraja_api.stk_push(
        #     phone=phone_number,
        #     amount=appt.consultation_fee,
        #     reference=f"APPT-{appointment_id}",
        # )
        # -----------------------------------------------------

        appt.payment_status  = "PENDING"
        appt.mpesa_reference = f"MOCK-MPESA-{appointment_id}"
        appt.save()

        logger.info(
            f"[MOCK M-Pesa] STK push sent to {phone_number} "
            f"for KES {appt.consultation_fee} — appointment {appointment_id}"
        )

    except Exception as exc:
        logger.error(f"M-Pesa task failed for appointment {appointment_id}: {exc}")
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Sends a welcome email to a newly registered patient.
    """
    try:
        from accounts.models import User
        user = User.objects.get(pk=user_id)

        subject = f"Welcome to {settings.SITE_NAME}!"
        message = (
            f"Dear {user.get_full_name()},\n\n"
            f"Welcome to {settings.SITE_NAME}!\n\n"
            f"Your patient account has been created successfully.\n"
            f"You can now book appointments with our doctors.\n\n"
            f"Visit us at: https://healthportal.andasy.dev\n\n"
            f"— The {settings.SITE_NAME} Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.info(f"Welcome email sent to {user.email}")

    except Exception as exc:
        logger.error(f"Failed to send welcome email to user {user_id}: {exc}")
        raise self.retry(exc=exc)
