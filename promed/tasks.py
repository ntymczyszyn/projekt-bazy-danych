from celery import shared_task
from .views import send_reminder_email_for_upcoming_appointments

@shared_task
def send_daily_reminder_emails():
    send_reminder_email_for_upcoming_appointments()
