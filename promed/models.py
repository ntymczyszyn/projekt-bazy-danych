from django.db import models
from django.conf import settings
import uuid
from datetime import datetime
from django.utils import timezone
from django.urls import reverse  # To generate URLS by reversing URL patterns
#from phonenumber_field.modelfields import PhoneNumberField <- czy się na to przerzucić
# phone_number = PhoneNumberField()

# models.py

# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     # Dodaj własne pola, jeśli są potrzebne

#     def save(self, *args, **kwargs):
#         if not self.username:  # Sprawdź, czy nazwa użytkownika jest pusta
#             base_username = f"{self.first_name}{self.last_name}".replace(" ", "")  # Połącz imię i nazwisko, usuń spacje
#             username = base_username

#             # Sprawdź, czy nazwa użytkownika już istnieje, i dodaj numer indeksu, jeśli trzeba
#             index = 1
#             while CustomUser.objects.filter(username=username).exists():
#                 index += 1
#                 username = f"{base_username}{index}"

#             self.username = username

#         super().save(*args, **kwargs)

class Doctor(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=9)

    def __str__(self) -> str:
        return f"{self.user_id.first_name} {self.user_id.last_name}"
    def get_absolute_url(self):
        return reverse('doctor-detail', args=[str(self.id)])

class Patient(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=9)
    date_of_birth = models.DateField()

    @property # metoda tylko do odczytu (atrybut obiektu)
    def age(self):
        today = datetime.now().date()
        birthdate = self.date_of_birth
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    # pesel validation?
    pesel = models.CharField(max_length=11, unique=True)
    def __str__(self) -> str:
        return f"{self.user_id.first_name} {self.user_id.last_name}"
    def get_absolute_url(self):
        return reverse('patient-detail', args=[str(self.id)])

class Facility(models.Model):
    street_address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=6)
    city = models.CharField(max_length=200)
    VOIVODESHIP_CHOICES = [
    ('dolnośląskie', 'dolnośląskie'),
    ('kujawsko-pomorskie', 'kujawsko-pomorskie'),
    ('lubelskie', 'lubelskie'),
    ('lubuskie', 'lubuskie'),
    ('łódzkie', 'łódzkie'),
    ('małopolskie', 'małopolskie'),
    ('mazowieckie', 'mazowieckie'),
    ('opolskie', 'opolskie'),
    ('podkarpackie', 'podkarpackie'),
    ('podlaskie', 'podlaskie'),
    ('pomorskie', 'pomorskie'),
    ('śląskie', 'śląskie'),
    ('świętokrzyskie', 'świętokrzyskie'),
    ('warmińsko-mazurskie', 'warmińsko-mazurskie'),
    ('wielkopolskie', 'wielkopolskie'),
    ('zachodniopomorskie', 'zachodniopomorskie'),
    ]
    voivodeship = models.CharField(max_length=20, choices=VOIVODESHIP_CHOICES) 

    class Meta:
        verbose_name_plural = "facilities"
    
    def __str__(self):
        return f"{self.street_address}, {self.city}"
    def get_absolute_url(self):
        return reverse('facility-detail', args=[str(self.id)])
    
class Specialization(models.Model):
    name = models.CharField(max_length=200, help_text='Podaj nazwę specjalizacji.')

    def __str__(self) -> str:
        return self.name
    def get_absolute_url(self):
        return reverse('specialization-detail', args=[str(self.id)])

class Service(models.Model):
    specialzation_id = models.ForeignKey('Specialization', on_delete=models.PROTECT) #on_delete=models.SET_NULL, null=True, blank=True
    doctor_id = models.ForeignKey('Doctor', on_delete=models.PROTECT) 
    DURATION_LENGTH = ( 
        ('15', '15 minut'),
        ('30', '30 minut')
    )
    duration = models.CharField(
        max_length=2, 
        choices=DURATION_LENGTH,
        default='30',
        help_text="Długość trwania usługi."
    )
    def __str__(self):
        return f"{self.specialzation_id}, {self.doctor_id}"
    def get_absolute_url(self):
        return reverse('service-detail', args=[str(self.id)])

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unikalne ID dla danej wizyty.")
    facility_id = models.ForeignKey('Facility', on_delete=models.PROTECT)
    service_id = models.ForeignKey('Service', on_delete=models.PROTECT)
    appointment_time = models.DateTimeField(default=timezone.now, null=True, blank=True) 
    APPOINTMENT_STATUS = (
        ('a', 'dostepna'),
        ('r', 'zarezerwowana'),
        ('c', 'zakonczona'), 
    )
    status = models.CharField(
        max_length=1, 
        choices=APPOINTMENT_STATUS,
        default='a',
        help_text="Status wizyty."
    )
    patient_id = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['appointment_time']
    
    def formatted_appointment_time(self):
        return self.appointment_time.strftime('%H:%M, %d-%m-%Y') if self.appointment_time else ''

    def __str__(self):
        formatted_time = self.formatted_appointment_time()
        return f"{self.service_id} [{formatted_time}] [{self.facility_id}]"
    def get_absolute_url(self):
        return reverse('appointment-detail', args=[str(self.id)])
