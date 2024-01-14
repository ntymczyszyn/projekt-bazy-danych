from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BD_projekt.settings')

app = Celery('BD_projekt')
# - namespace='CELERY' means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc = False
app.conf.update(timezone = 'Europe/Warsaw')

app.conf.beat_schedule = {
    'send-appointment-remainder-mail-every-day': {
        'task': 'promed.tasks.send_email_appointment_reminder',
        'schedule': crontab(hour=23, minute=59),
    }
}

# celery -A BD_projekt worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
# celery -A BD_projekt beat -l INFO

app.conf.beat_schedule = {
    'Send_mail_to_Client': {
    'task': 'promed.tasks.send_email_appointment_confirmation',
    'schedule': 30.0, #every 30 seconds it will be called
    }
}
# Load task modules from all registered Django apps.
app.autodiscover_tasks()
