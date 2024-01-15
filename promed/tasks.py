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
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.conf import settings

@shared_task(serializer='json', name="send_appointment_confirmation_mail")
def send_email_appointment_confirmation(recipient, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        subject = 'Potwierdzenie wizyty'
        html_message = render_to_string('email/appointment_confirmation_email.html', {
            'appointment': appointment,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = recipient

        send_mail(
            subject,
            plain_message,  # Tekstowa wersja e-maila
            from_email,
            [recipient_email],
            html_message=html_message,  # HTMLowa wersja e-maila
        )

        return "Wysłano maila z potwierdzeniem rezerwacji!"
    except Appointment.DoesNotExist:
        return "Błąd: Wizyta nie istnieje."

@shared_task(serializer='json', name="send_appointment_cancel_mail")
def send_email_appointment_cancel(recipient, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        subject = 'Odwołanie wizyty'
        html_message = render_to_string('email/appointment_cancel_email.html', {
            'appointment': appointment,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = recipient

        send_mail(
            subject,
            plain_message,  
            from_email,
            [recipient_email],
            html_message=html_message, 
        )
        return "Wysłano maila z info o odwołaniu wizyty"
    except Appointment.DoesNotExist:
        return "Błąd: Wizyta nie istnieje."

# @shared_task
# def send_welcome_email_patient(recipient_email, username):
#     subject = 'Witamy w Promed'
#     html_message = render_to_string('email/welcome_email_.html', 
#                                     {'username': username})
#     plain_message = strip_tags(html_message)
#     from_email = settings.DEFAULT_FROM_EMAIL
   
#     send_mail(
#                 subject,
#                 plain_message,  
#                 from_email,
#                 [recipient_email],
#                 html_message=html_message, 
#             )
