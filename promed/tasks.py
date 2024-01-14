# 1. w osobnym terminalu
# celery -A BD_projekt worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
# 2. no i w wsl musi być aktywny redis; instalowanie:
#  sudo apt-add-repository ppa:redislabs/redis
#  sudo apt-get update
#  sudo apt-get upgrade
#  sudo apt-get install redis-server
# przydatne:  sudo service redis-server restart
# sprrawdzenie czy działa: redis-cli

# celery -A BD_projekt beat -l INFO
from celery import shared_task
from django.core.mail import send_mail
import time
import json


from .models import Appointment, Patient, Doctor, Service, Specialization, Facility
from django.utils import timezone
from django.template.loader import render_to_string

@shared_task(serializer='json', name="send_appointment_confirmation_mail")
def send_email_test():    
    return "Wysłano maila!"

@shared_task(serializer='json', name="send_appointment_confirmation_mail")
def send_email_appointment_confirmation(subject, message, sender, receiver):    
    send_mail(subject, message, sender, [receiver])
    return "Wysłano maila!"

# codzienne przypomnienia o 23.59
@shared_task(bind=True, serializer='json', name="send_appointment_reminder_mail")
def send_email_appointment_reminder(self):
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    appointments = Appointment.objects.filter(status='b', appointment_time__date=tomorrow)

    for appointment in appointments:
        subject = 'Nadchodząca wizyta w Promed'
        html_message = render_to_string('appointment_reminder_email.html', {
            'doctor_name': appointment.service_id.doctor_id,
            'doctor_specialization': appointment.service_id.doctor_id.specialization_id.name,
            'appointment_date': appointment.appointment_time.strftime('%Y-%m-%d %H:%M'),
            'facility_name': appointment.facility_id,
        })
        from_email = 'promed.administration@promed.pl'
        recipient_email = appointment.patient_id.user_id.email if appointment.patient_id.user_id.email else ''

        if recipient_email:
            recipient_list = [recipient_email]
            send_mail(subject, '', from_email, recipient_list, html_message=html_message)

    return "Reminder email sent. :)"