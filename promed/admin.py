from django.contrib import admin
from .models import Facility, Service, Appointment, Specialization, Patient, Doctor

admin.site.site_header = "Promed administration"

admin.site.register(Facility)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Specialization)
admin.site.register(Doctor)
admin.site.register(Patient)