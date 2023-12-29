from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Patient, Doctor, Service
from .forms import AppointmentSearchForm

'''
HOME
- do tworzenia konta
- do logowana
PACJENT
- do odzyskiwania hasła
- do przeglądanie odbywanych wizyt (nadchodzących i przeszłych)
- do rezerwacji wizyty
- do anulowania wizyty
LEKARZ
- do deklarowanie dyspozyjności
- do przeglądania wykonywanych wizyt (nadchodzących i przeszłych)
'''
def home(request):
    return render(request, 'home.html')


# wyświetlanie wszystkich wizyt u zalogwanego użytownika, ktróry jest pacjentem
class AppointmentsByUserListView(LoginRequiredMixin, generic.ListView):
    model = Appointment
    template_name = 'promed/appointment_list_user.html'
    # paginate_by = 10 # trzeba będzie dodać do base_html  {% block pagination %}

    def get_queryset(self):
        patient = get_object_or_404(Patient, user_id=self.request.user)
        
        return (
            Appointment.objects.filter(patient_id=patient)
            .order_by('appointment_time')
        )

class PatientDetailView(LoginRequiredMixin, generic.DetailView):
    def get(self, request):
        patient = Patient.objects.get(user_id=request.user)
        context = {
            'first_name': patient.user_id.first_name,
            'last_name': patient.user_id.last_name,
            'phone_number': patient.phone_number,
            'pesel': patient.pesel,
        }
        return render(request, 'promed/patient_detail.html', context)

#APPOINTMENTS
class ReservationAppointmentsView(LoginRequiredMixin, generic.ListView):
    model = Appointment
    template_name = 'promed/reservation_appointments.html'
    # paginate_by = 10 # trzeba będzie dodać do base_html  {% block pagination %}

    def get_queryset(self):
        available = 'a'
        return (
            Appointment.objects.filter(status=available)
            .order_by('appointment_time')
        )

#DOCTORS
class AppointmentsByDoctorListView(LoginRequiredMixin, generic.ListView):
    model = Appointment
    template_name = 'promed/appointment_list_doctor.html'
    # paginate_by = 10 # trzeba będzie dodać do base_html  {% block pagination %}

    def get_queryset(self):
        # id_user = get_object_or_404(Patient, user_id=self.request.user)
        doctor = get_object_or_404(Doctor, user_id = self.request.user)
        return (
            Appointment.objects.filter(service_id__doctor_id=doctor)
            .order_by('appointment_time')
        )

class DoctorDetailView(LoginRequiredMixin, generic.DetailView):
    def get(self, request):
        doctor = Doctor.objects.get(user_id=request.user)
        context = {
            'first_name': doctor.user_id.first_name,
            'last_name': doctor.user_id.last_name,
            'phone_number': doctor.phone_number,
        }
        return render(request, 'promed/doctor_detail.html', context)

# WYSZUKIWARKA
class AppointmentSearchView(View):
    def get(self, request):
        form = AppointmentSearchForm(request.GET)
        appointments = Appointment.objects.all()

        if form.is_valid():
            doctor = form.cleaned_data.get('doctor')
            facility = form.cleaned_data.get('facility')

            if doctor:
                appointments = appointments.filter(service_id__doctor_id=doctor)
            if facility:
                appointments = appointments.filter(facility_id=facility)

        return render(request, 'appointment_search_results.html', {'form': form, 'appointments': appointments})
    
# LOGOWANIE, RESETOWANIE HASŁA
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy

class PatientLoginView(LoginView):
    def get_success_url(self):
        # Pobierz użytkownika, który został właśnie zalogowany
        user = self.request.user
        if hasattr(user, 'patient'):
            return reverse_lazy('patient_dashboard')
        else:
            return reverse_lazy('patient_access_denied') 

    def form_valid(self, form):
        # Pobierz użytkownika, który próbuje się zalogować
        user = form.get_user()
        if hasattr(user, 'patient'):
            return super().form_valid(form)
        else:
            form.add_error(None, 'Tylko pacjenci mogą się zalogować.')
            return self.form_invalid(form)

    def get(self, *args, **kwargs):
        # Jeśli użytkownik jest już zalogowany, przekieruj go na pateint dashboard
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(*args, **kwargs)


def pateint_access_denied(request):
    return render(request, 'registration/patient_access_denied.html')

# class CustomLogoutView(LogoutView):

# class CustomPasswordChangeView(PasswordChangeView):

# class CustomPasswordResetView(PasswordResetView):

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):

# TWORZENIE PACJENTA

from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .signals import user_registered_patient_site

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_registered_patient_site.send(sender=user.__class__, user=user, created=True)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
