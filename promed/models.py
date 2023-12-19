from django.db import models
from django.conf import settings
import uuid
from datetime import date
from django.urls import reverse  # To generate URLS by reversing URL patterns
#from phonenumber_field.modelfields import PhoneNumberField <- czy się na to przerzucić
# phone_number = PhoneNumberField()
# TO-DO:
# sprawdź on_delete, dopisz help_text
# funkcje Meta?
class Doctor(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=9)

    def __str__(self) -> str:
        return f"{self.user_id.first_name} {self.user_id.last_name}"
    def get_absolute_url(self):
        """Returns the url to access a particular doctor instance."""
        return reverse('doctor-detail', args=[str(self.id)])

class Patient(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=9)
    date_of_birth = models.DateField()
    # liczyć wiek jako @property??
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
    specialzation_id = models.ForeignKey('Specialization', on_delete=models.SET_NULL, null=True) #on_delete=models.SET_NULL, null=True, blank=True
    doctor_id = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True)
    DURATION_LENGTH = ( # narazie tylko 2 rodzaje
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
    facility_id = models.ForeignKey('Facility', on_delete=models.SET_NULL, null=True)
    service_id = models.ForeignKey('Service',on_delete=models.SET_NULL, null=True)
    appointment_time = models.DateTimeField(null=True, blank=True) 
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
