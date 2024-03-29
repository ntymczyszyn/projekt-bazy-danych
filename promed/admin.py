from django.contrib import admin
from .models import Facility, Service, Appointment, Specialization, Patient, Doctor

admin.site.site_header = "Promed administration"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form_template = 'admin/custom_user_add_form.html'

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

    fieldsets = (
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
            (
                None,
                {
                    'classes': ('wide',),
                    'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
                },
            ),
        )

admin.site.register(Facility)
admin.site.register(Service)
admin.site.register(Specialization)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_filter = ('status', 'appointment_time', 'service_id__specialzation_id', 'service_id__doctor_id', 'facility_id')


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