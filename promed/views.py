from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Patient, Doctor, Service, Specialization, Facility
from .forms import AppointmentSearchForm, PatientInfoForm, CustomUserCreationForm, AvailabilityForm, SpecializationSearchForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy, reverse
from .signals import user_registered_patient_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class MyLogoutView(LogoutView):
    next_page = '/promed/accounts/logout/'
    allowed_methods = ['get']

def custom_logout(request):
    return render(request, 'logged_out.html')

def home_view(request):
    return render(request, 'home.html')

def home_patient_view(request):
    return render(request, 'home_patient.html')

def home_doctor_view(request):
    return render(request, 'home_doctor.html')


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@login_required
def patient_dashboard_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)

    search_future = request.GET.get('search_future', '')
    search_past = request.GET.get('search_past', '')

    if not (patient.phone_number and patient.date_of_birth and patient.pesel):
        return redirect('complete_patient_info')
    
    all_appointments = (
        Appointment.objects.filter(patient_id=patient)
        .order_by('appointment_time')
    )
    # czy ten podział też ze względu na zarezerwowanie i potwierdzoen nie powinien być ?? a nie tak tylko po czasie
    past_appointments = [appointment for appointment in all_appointments if appointment.appointment_time < timezone.now()]
    future_appointments = [appointment for appointment in all_appointments if appointment.appointment_time >= timezone.now()]

    if search_future:
        future_appointments = [appointment for appointment in future_appointments 
                               if search_future.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_future.lower() in appointment.service_id.doctor_id.user_id.first_name.lower() 
                               or search_future.lower() in appointment.service_id.doctor_id.user_id.last_name.lower()
                               or search_future.lower() in appointment.facility_id.street_address.lower() 
                               or search_future.lower() in appointment.facility_id.postal_code.lower() 
                               or search_future.lower() in appointment.facility_id.city.lower() 
                               or search_future.lower() in appointment.facility_id.voivodeship.lower()]
    if search_past:
        past_appointments = [appointment for appointment in past_appointments 
                               if search_past.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_past.lower() in appointment.service_id.doctor_id.user_id.first_name.lower() 
                               or search_past.lower() in appointment.service_id.doctor_id.user_id.last_name.lower()
                               or search_past.lower() in appointment.facility_id.street_address.lower() 
                               or search_past.lower() in appointment.facility_id.postal_code.lower() 
                               or search_past.lower() in appointment.facility_id.city.lower() 
                               or search_past.lower() in appointment.facility_id.voivodeship.lower()]
    
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

def send_welcome_email_patient(user_email, username):
    subject = 'Witamy w Promed'
    html_message = render_to_string('registration/pateint/welcome_email_.html', {'username': username})
    plain_message = strip_tags(html_message)
    from_email = 'promed.administration@promed.pl'
    recipient_list = [user_email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

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

    search_reserved = request.GET.get('search_reserved', '')
    search_available = request.GET.get('search_available', '')
    search_past = request.GET.get('search_past', '')

    # Pobieramy wszystkie wizyty lekarza
    all_appointments = (
        Appointment.objects.filter(service_id__doctor_id=doctor)
        .order_by('service_id__specialzation_id','facility_id','appointment_time')
    )

    # Dzielimy wizyty na przeszłe i nadchodzące one od syatusu powinny zależeć a nie od czasu
    past_appointments = [appointment for appointment in all_appointments if appointment.appointment_time < timezone.now()]
    future_appointments = [appointment for appointment in all_appointments if appointment.appointment_time >= timezone.now()]

    # Dzielimy nadchodzące wizyty na zarezerwowane i dostępne i potwierdzone
    reserved_appointments = [appointment for appointment in future_appointments if (appointment.status == 'b' or appointment.status == 'c')]
    available_appointments = [appointment for appointment in future_appointments if appointment.status == 'a']

    if search_available:
        available_appointments = [appointment for appointment in available_appointments 
                               if  search_available.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_available.lower() in appointment.facility_id.street_address.lower() 
                               or search_available.lower() in appointment.facility_id.postal_code.lower() 
                               or search_available.lower() in appointment.facility_id.city.lower() 
                               or search_available.lower() in appointment.facility_id.voivodeship.lower()]
    
    if search_reserved:
        reserved_appointments = [appointment for appointment in reserved_appointments 
                               if  search_reserved.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_reserved.lower() in appointment.facility_id.street_address.lower() 
                               or search_reserved.lower() in appointment.facility_id.postal_code.lower() 
                               or search_reserved.lower() in appointment.facility_id.city.lower() 
                               or search_reserved.lower() in appointment.facility_id.voivodeship.lower()]
    if search_past:
        past_appointments = [appointment for appointment in past_appointments 
                               if search_past.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_past.lower() in appointment.facility_id.street_address.lower() 
                               or search_past.lower() in appointment.facility_id.postal_code.lower() 
                               or search_past.lower() in appointment.facility_id.city.lower() 
                               or search_past.lower() in appointment.facility_id.voivodeship.lower()]
    
    return render(
        request,
        'doctor_dashboard.html',
        {
            'past_appointments': past_appointments,
            'reserved_appointments': reserved_appointments,
            'available_appointments': available_appointments,
        }
    )

class PatientPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Hasło zostało pomyślnie zmienione.')
        return response

    def get_success_url(self):
        return reverse_lazy('patient_dashboard')  

class DoctorPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'  

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Hasło zostało pomyślnie zmienione.')
        return response

    def get_success_url(self):
        return reverse_lazy('doctor_dashboard') 
    
@login_required
def doctor_past_appointments_view(request):
    doctor = get_object_or_404(Doctor, user_id=request.user)

    # Pobieramy przeszłe wizyty lekarza
    past_appointments = (
        Appointment.objects.filter(
            service_id__doctor_id=doctor,
            appointment_time__lt=timezone.now()
        )
        .order_by('service_id__specialzation_id', 'status', 'appointment_time')
        .select_related('patient_id')
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

from datetime import datetime, timedelta

@login_required
def doctor_availability(request):
    template_name = 'set_availability.html'
    doctor = Doctor.objects.get(user_id=request.user)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST, doctor=doctor)

        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            duration = form.cleaned_data['duration']
            selected_specialization = form.cleaned_data['specialization']
            selected_date = form.cleaned_data['selected_date']
            selected_facility = form.cleaned_data['facility']

            current_time = start_time
            current_datetime = datetime.combine(selected_date, current_time)
            end_datetime = datetime.combine(selected_date, end_time)

            while current_datetime < end_datetime:
                try:
                    service = Service.objects.get(
                            specialzation_id=selected_specialization,
                            doctor_id=doctor,
                            duration=duration
                    )
                    availability = Appointment(
                        appointment_time=current_datetime,
                        service_id=service,
                        facility_id=selected_facility,
                        status='a',
                    )
                    availability.save()
                    current_datetime += timedelta(minutes=int(duration))
                except Service.DoesNotExist:
                    # Obsłuż sytuację, gdy nie istnieje usługa dla danej specjalizacji i lekarza
                    messages.error(request, f'Nie istnieje usługa dla specjalizacji {selected_specialization} i lekarza {doctor}.')
                    return redirect('doctor_dashboard')

            messages.success(request, 'Dostępność wprowadzona prawidłowo.')
            return redirect('doctor_dashboard')
    else:
        form = AvailabilityForm(doctor=doctor)

    return render(request, template_name, {'form': form})


@login_required
def appointment_search_specialization_view(request):
    form =  SpecializationSearchForm(request.GET)
    specializations = Specialization.objects.all()

    if form.is_valid():
        specialization = form.cleaned_data.get('specialization')
        if specialization:
            return redirect('appointment_search', specialization_id=specialization.id)

    return render(request, 'appointments_research_specialization.html', {'form': form, 'specializations': specializations})

@login_required
def appointment_search_patient_view(request,specialization_id):
    specialization = get_object_or_404(Specialization, id=specialization_id)
    services = Service.objects.filter(specialzation_id=specialization)
    doctor = Doctor.objects.filter(service__in=services)

    form = AppointmentSearchForm(request.GET, doctor=doctor)
    appointments = []

    if request.method == 'GET' and form.is_valid():
        doctor = form.cleaned_data.get('doctor')
        facility = form.cleaned_data.get('facility')
        date = form.cleaned_data.get('date')
        time_slot = form.cleaned_data.get('time_slot')
        appointments = Appointment.objects.filter(status='a')

        if doctor:
            appointments = appointments.filter(service_id__doctor_id=doctor)
        if facility:
            appointments = appointments.filter(facility_id=facility)
        if date:
            appointments = appointments.filter(appointment_time__date=date)

        # Ustaw odpowiednie przedziały czasowe
        if time_slot == '7-12':
            appointments = appointments.filter(appointment_time__time__gte='07:00', appointment_time__time__lt='12:00')
        elif time_slot == '12-17':
            appointments = appointments.filter(appointment_time__time__gte='12:00', appointment_time__time__lt='17:00')
        elif time_slot == '17-20':
            appointments = appointments.filter(appointment_time__time__gte='17:00', appointment_time__time__lt='20:00')
        elif time_slot == 'all':
            appointments = appointments.filter(appointment_time__time__gte='07:00', appointment_time__time__lt='20:00')


    return render(request, 'appointments_research_results.html', {'form': form, 'appointments': appointments, 'specialization':specialization})

def confirm_book_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_booking.html', {'appointment': appointment,})

from django.contrib import messages
#  Do confirm
def confirmation_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_confirm.html', {'appointment': appointment,})

def confirm_confirmation_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    try:
        appointment.status = 'c'  
        appointment.save()
        messages.success(request, 'Potwierdzono wizytę')
    except Exception as e:
        messages.error(request, f'Błąd podczas potwierdzania wizyty: {str(e)}')

    return redirect(reverse('patient_dashboard'))
# 


def complete_book_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)

    try:
        patient = request.user.patient
        appointment.patient_id = patient
        appointment.status = 'b'  
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

def confirm_appointment_doctor_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointments_doctor_confirm.html', {'appointment': appointment,})

def confirm_appointment_doctor_done_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    try:
        appointment.status = 'd'  
        appointment.save()
        messages.success(request, 'Zrealizowano wizytę.')
    except Exception as e:
        messages.error(request, f'Błąd podczas zmiany statusu wizyty: {str(e)}')

    return redirect(reverse('doctor_dashboard'))


def send_appointment_reminder_email(recipient_email, appointment):
    pass

def send_reminder_email_for_upcoming_appointments():
    # Pobierz wszystkie zarezerwowane wizyty na następny dzień
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    appointments = Appointment.objects.filter(status='b', appointment_time__date=tomorrow)

    for appointment in appointments:
        subject = 'Nadchodząca wizyta w Promed'
        html_message = render_to_string('appointment_reminder_email.html', {
            'doctor_name': appointment.service_id.doctor_id,
            'doctor_specialization': appointment.service_id.doctor_id.specialization_id.name,
            'appointment_date': appointment.appointment_time.strftime('%Y-%m-%d %H:%M'),
            'facility_name': appointment.facility_id,
        })
        from_email = 'promed.administration@promed.pl'
        recipient_email = appointment.patient_id.user_id.email if appointment.patient_id.user_id.email else ''

        if recipient_email:
            recipient_list = [recipient_email]
            send_mail(subject, '', from_email, recipient_list, html_message=html_message)


# INNE
class FacilityDetailView(generic.DetailView):
    model = Facility
    template_name = 'facility_detail.html'   

class AppointmentDetailView(generic.DetailView):
    model = Appointment
    template_name = 'appointment_detail.html'
    context_object_name = 'appointment'

class AppointmentDetailDoctorView(generic.DeleteView):
    model = Appointment
    template_name = 'appointment_detail_doctor.html'
    context_object_name = 'appointment'