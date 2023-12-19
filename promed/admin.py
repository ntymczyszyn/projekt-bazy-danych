from django.contrib import admin
from .models import Facility, Service, Appointment, Specialization, Patient, Doctor

admin.site.site_header = "Promed administration"

admin.site.register(Facility)
admin.site.register(Service)
admin.site.register(Specialization)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):  
    list_filter = ('appointment_time', 'facility_id')

class ServiceInline(admin.TabularInline):
    model = Service

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):  
    inlines = [ServiceInline]

class AppointmentInline(admin.TabularInline):
    model = Appointment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):  
    inlines = [AppointmentInline]