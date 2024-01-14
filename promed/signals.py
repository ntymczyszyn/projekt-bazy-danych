from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver, Signal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Patient

user_registered_patient_site = Signal()

@receiver(user_registered_patient_site)        
def create_patient(sender, user, created, **kwargs):
    if created:
        Patient.objects.create(user_id=user)

