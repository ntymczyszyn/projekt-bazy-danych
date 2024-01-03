from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Patient, Doctor, Service, Specialization, Facility
from .forms import AppointmentSearchForm, PatientInfoForm, CustomUserCreationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy, reverse
from .signals import user_registered_patient_site
from django.core.mail import send_mail
'''
LEKARZ
- do deklarowanie dyspozyjności
- do przeglądania wykonywanych wizyt (nadchodzących i przeszłych)
'''
def custom_logout(request):
    return render(request, 'logged_out.html')

def home_view(request):
    return render(request, 'home.html')

def home_patient_view(request):
    return render(request, 'home_patient.html')

def home_doctor_view(request):
    return render(request, 'home_doctor.html')

@login_required
def patient_dashboard_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)

    # Sprawdzamy, czy pacjent ma uzupełnione dane
    if not (patient.phone_number and patient.date_of_birth and patient.pesel):
        # Jeśli nie, przekierowujemy do formularza uzupełnienia
        return redirect('complete_patient_info')
    
    # Pobieramy wszystkie wizyty pacjenta
    all_appointments = (
        Appointment.objects.filter(patient_id=patient)
        .order_by('appointment_time')
    )

    # Dzielimy wizyty na przeszłe i nadchodzące
    past_appointments = [appointment for appointment in all_appointments if appointment.appointment_time < timezone.now()]
    future_appointments = [appointment for appointment in all_appointments if appointment.appointment_time >= timezone.now()]

    return render(
        request,
        'patient_dashboard.html',
        {
            'past_appointments': past_appointments,
            'future_appointments': future_appointments,
        }
    )

@login_required
def complete_info_patient_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)

    if patient.phone_number and patient.date_of_birth and patient.pesel:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientInfoForm(request.POST)
        if form.is_valid():
            patient.phone_number = form.cleaned_data['phone_number']
            patient.date_of_birth = form.cleaned_data['date_of_birth']
            patient.pesel = form.cleaned_data['pesel']
            patient.save()
            return redirect('patient_dashboard')
    else:
        form = PatientInfoForm()

    return render(request, 'complete_patient_info.html', {'form': form})

@login_required
def patient_detail_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)
    context = {
        'first_name': patient.user_id.first_name,
        'last_name': patient.user_id.last_name,
        'phone_number': patient.phone_number,
        'pesel': patient.pesel,
    }
    return render(request, 'patient_detail.html', context)

class PatientLoginView(LoginView):
    template_name = 'registration/patient/login_patient.html'
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

def patient_access_denied_view(request):
    return render(request, 'registration/patient/patient_access_denied.html')

# class CustomLogoutView(LogoutView):

# class CustomPasswordChangeView(PasswordChangeView):

# class CustomPasswordResetView(PasswordResetView):

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):

def send_welcome_email_patient(user_email): # czy to moża było jako html zrobić?
    subject = 'Witamy w Promed'
    message = 'Dziękujemy za rejestracje. Pamiętaj o uzupełnieniu swojego profilu po pierwszym logowaniu.'
    from_email = 'promed.administation@promed.pl'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

def register_patient_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_registered_patient_site.send(sender=user.__class__, user=user, created=True)
            send_welcome_email_patient(user.email)
            return redirect('home_patient')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/patient/register_patient.html', {'form': form})

# DOCTOR SITE-----------------------------------------------------------------------------
class DoctorLoginView(LoginView):
    template_name = 'registration/doctor/login_doctor.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'doctor'):
            return reverse_lazy('doctor_dashboard')
        else:
            return reverse_lazy('doctor_access_denied') 

    def form_valid(self, form):
        # Pobierz użytkownika, który próbuje się zalogować
        user = form.get_user()
        if hasattr(user, 'doctor'):
            return super().form_valid(form)
        else:
            form.add_error(None, 'Tylko pracownicy mogą się zalogować.')
            return self.form_invalid(form)

    def get(self, *args, **kwargs):
        # Jeśli użytkownik jest już zalogowany, przekieruj go na pateint dashboard
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(*args, **kwargs)
    
def doctor_access_denied_view(request):
    return render(request, 'registration/doctor/doctor_access_denied.html')

@login_required
def doctor_dashboard_view(request):
    doctor = get_object_or_404(Doctor, user_id=request.user)

    # Pobieramy wszystkie wizyty lekarza
    all_appointments = (
        Appointment.objects.filter(service_id__doctor_id=doctor)
        .order_by('appointment_time')
    )

    # Dzielimy wizyty na przeszłe i nadchodzące
    past_appointments = [appointment for appointment in all_appointments if appointment.appointment_time < timezone.now()]
    future_appointments = [appointment for appointment in all_appointments if appointment.appointment_time >= timezone.now()]

    # Dzielimy nadchodzące wizyty na zarezerwowane i dostępne
    reserved_appointments = [appointment for appointment in future_appointments if appointment.status == 'r']
    available_appointments = [appointment for appointment in future_appointments if appointment.status == 'a']

    return render(
        request,
        'doctor_dashboard.html',
        {
            'past_appointments': past_appointments,
            'reserved_appointments': reserved_appointments,
            'available_appointments': available_appointments,
        }
    )

@login_required
def doctor_past_appointments_view(request):
    doctor = get_object_or_404(Doctor, user_id=request.user)

    # Pobieramy przeszłe wizyty lekarza
    past_appointments = (
        Appointment.objects.filter(
            service_id__doctor_id=doctor,
            appointment_time__lt=timezone.now()
        )
        .order_by('appointment_time')
    )

    return render(
        request,
        'doctor_past_appointments.html',
        {
            'past_appointments': past_appointments,
        }
    )


@login_required
def doctor_detail_view(request):
    doctor = get_object_or_404(Doctor, user_id=request.user)
    services = Service.objects.filter(doctor_id=doctor)
    specializations = Specialization.objects.filter(service__in=services).distinct()

    context = {
        'doctor': doctor,
        'specializations': specializations,
    }
    return render(request, 'doctor_detail.html', context)

@login_required
def appointment_search_patient_view(request):
    form = AppointmentSearchForm(request.GET)
    appointments = []

    if form.is_valid():
        doctor = form.cleaned_data.get('doctor')
        facility = form.cleaned_data.get('facility')
        specialization = form.cleaned_data.get('specialization')
        date = form.cleaned_data.get('date')
        start_time = form.cleaned_data.get('start_time')
        end_time = form.cleaned_data.get('end_time')

        appointments = Appointment.objects.filter(status='a')
        if doctor:
            appointments = appointments.filter(service_id__doctor_id=doctor)
        if facility:
            appointments = appointments.filter(facility_id=facility)
        if specialization:
            appointments = appointments.filter(service_id__specialzation_id=specialization)
        if date:
            appointments = appointments.filter(appointment_time__date=date)
        if start_time:
            appointments = appointments.filter(appointment_time__time__gte=start_time)
        if end_time:
            appointments = appointments.filter(appointment_time__time__lte=end_time)

    return render(request, 'appointments_research_results.html', {'form': form, 'appointments': appointments})

def confirm_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_booking.html', {'appointment': appointment,})

from django.contrib import messages

def complete_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)

    try:
        patient = request.user.patient
        appointment.patient_id = patient
        appointment.status = 'r'  
        appointment.save()
        messages.success(request, 'Rezerwacja zakończona pomyślnie.')
    except Exception as e:
        messages.error(request, f'Błąd podczas rezerwacji: {str(e)}')

    return redirect(reverse('patient_dashboard'))

def cancel_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_cancellation.html', {'appointment': appointment,})

def confirm_cancel_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    try:
        appointment.patient_id = None
        appointment.status = 'a'  
        appointment.save()
        messages.success(request, 'Anulowano wizytę.')
    except Exception as e:
        messages.error(request, f'Błąd podczas odwływania wizyty: {str(e)}')

    return redirect(reverse('patient_dashboard'))

# INNE
class FacilityDetailView(generic.DetailView):
    model = Facility
    template_name = 'facility_detail.html'   

class AppointmentDetailView(generic.DetailView):
    model = Appointment
    template_name = 'appointment_detail.html'
    context_object_name = 'appointment'