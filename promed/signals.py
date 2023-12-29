from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver, Signal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Patient

user_registered_patient_site = Signal()

@receiver(user_registered_patient_site)        
def create_patient(sender, user, created, **kwargs):
    if created:
        # group = Group.objects.get(name='Patient')  # Załóż, że masz grupę o nazwie 'Patient'
        # instance.groups.add(group)
        Patient.objects.create(user_id=user)

# User = get_user_model()

# @receiver(pre_save, sender=User)
# def create_username(sender, instance, **kwargs):
#     if not instance.username:
#         base_username = f"{instance.first_name}{instance.last_name}"
#         username = base_username
#         count = 1
#         while User.objects.filter(username=username).exists():
#             username = f"{base_username}{count}"
#             count += 1
#         instance.username = username