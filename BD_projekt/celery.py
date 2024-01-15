from __future__ import absolute_import, unicode_literals
import os
from django import setup
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
# celery -A BD_projekt worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
# celery -A BD_projekt beat -l INFO

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BD_projekt.settings')
setup()
from promed.models import Appointment, Patient, Doctor, Service, Specialization, Facility

app = Celery('BD_projekt')
# - namespace='CELERY' means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc = False
app.conf.update(timezone = 'Europe/Warsaw')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=23, minute=59),
        send_email_appointment_reminder, name="send_appointment_reminder_mail"
    )
    sender.add_periodic_task(
        crontab(hour=0, minute=1),
        send_email_appointment_reminder, name="change_unused_appointments_status"
    )

@app.task
def send_email_appointment_reminder():

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    appointments = Appointment.objects.filter(status='b', appointment_time__date=tomorrow)

    for appointment in appointments:
        subject = 'Nadchodząca wizyta w Promed'
        html_message = render_to_string('appointment_reminder_email.html', {
            'doctor_name': appointment.service_id.doctor_id,
            'doctor_specialization': appointment.service_id.specialzation_id.name,
            'appointment_date': appointment.appointment_time.strftime('%Y-%m-%d %H:%M'),
            'facility_name': appointment.facility_id,
        })
        from_email = 'promed.administration@promed.pl'
        recipient_email = appointment.patient_id.user_id.email if appointment.patient_id.user_id.email else ''

        if recipient_email:
            recipient_list = [recipient_email]
            send_mail(subject, '', from_email, recipient_list, html_message=html_message)

    return "Reminder email sent. :)"

@app.task
def change_unused_appointments_status():
    yesterday = timezone.now() - timezone.timedelta(days=1)
    appointments_to_change = Appointment.objects.filter(
        status='a',  
        appointment_time__date=yesterday.date()
    )
    appointments_to_change.update(status='u') 


app.autodiscover_tasks()

