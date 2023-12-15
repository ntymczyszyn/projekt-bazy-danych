from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from datetime import date
#from phonenumber_field.modelfields import PhoneNumberField
#**********************************************
# trzeba utworzyć folder promed/migrations
# a w nim touch __init.py__, żeby migrcje zaczeły działać
#***************************************
# TO-DO
# ustal co się ma dziać on_delete, dopisać help_text
# sprawdzić czy ta biblioteka phonemunber_field jest git
# pododawać funkcje __str__(self) i get_absolute_url(self) i Meta
class Doctor(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #phone_number = PhoneNumberField() # weź to jeszcze sprawdź
    # to jeszcze do okiełznania jakoś
    phone_number = models.CharField(max_length=9)
    # czy tak lepiej to robić?
    # borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class Patient(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=9)
    date_of_birth = models.DateField()
    # czy tu liczyć wiek jako @property??
    # czy robić pesel validation?
    pesel = models.CharField(max_length=11, unique=True)

class Facility(models.Model):
    street_address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=6)
    city = models.CharField(max_length=200)
    voivodeship = models.CharField(max_length=20) # jeśli nie uwzględniamy słowa "województwo"

    class Meta:
        verbose_name_plural = "facilities"
    
    def __str__(self):
        return self.street_address
    
class Specialization(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a specialization name.')

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    specialzation_id = models.ForeignKey('Specialization', on_delete=models.SET_NULL, null=True)
    doctor_id = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True)
    DURATION_LENGTH = ( # narazie tylko te 2 dodałam
        ('15', '15 minutes'),
        ('30', '30 minutes')
    )
    duration = models.CharField(
        max_length=2, 
        choices=DURATION_LENGTH,
        default='30',
        help_text="Service duration. (choose form predefined values)"
    )

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular appointment.")
    facility_id = models.ForeignKey('Facility', on_delete=models.SET_NULL, null=True)
    service_id = models.ForeignKey('Service',on_delete=models.SET_NULL, null=True)
    appointment_time = models.DateField(null=True, blank=True)
    APPOINTMENT_STATUS = (
        ('a', 'avaliable'),
        ('r', 'reserved'),
        ('c', 'completed'), 
    )
    status = models.CharField(
        max_length=1, 
        choices=APPOINTMENT_STATUS,
        default='a',
        help_text="Appointment status."
    )
    patient_id = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True)

