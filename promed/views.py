from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Appointment, Patient, Doctor, Service, Specialization, Facility
from .forms import PatientUpdateInfoForm, AppointmentSearchForm, PatientInfoForm, CustomUserCreationForm, AvailabilityForm, SpecializationSearchForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy, reverse
from .signals import user_registered_patient_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from .tasks import send_email_appointment_confirmation, send_email_appointment_cancel
from django.db import transaction
from django.conf import settings

class MyLogoutView(LogoutView):
    next_page = '/promed/accounts/logout/'
    allowed_methods = ['get']

def custom_logout(request):
    return render(request, 'logged_out.html')

def home_view(request):
    return render(request, 'home.html')

def home_patient_view(request):
    return render(request, 'home_patient.html')

def home_staff_view(request):
    return render(request, 'home_doctor.html')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
# PATIENT SITE ----------------------------------------------------------------------------
@login_required
def patient_dashboard_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)

    search_booked = request.GET.get('search_booked', '')
    search_confirmed = request.GET.get('search_confirmed', '')
    search_past = request.GET.get('search_past', '')

    if not (patient.phone_number and patient.date_of_birth and patient.pesel):
        return redirect('complete_patient_info')
    
    all_appointments = (
        Appointment.objects.filter(patient_id=patient)
        .order_by('appointment_time')
    )
    # czy ten podział też ze względu na zarezerwowanie i potwierdzoen nie powinien być ?? a nie tak tylko po czasie
    past_appointments = [appointment for appointment in all_appointments if appointment.status == 'd']
    booked_appointments = [appointment for appointment in all_appointments if appointment.status == 'b']
    confirmed_appointments = [appointment for appointment in all_appointments if appointment.status == 'c']

    if search_booked:
        booked_appointments = [appointment for appointment in booked_appointments 
                               if search_booked.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_booked.lower() in appointment.service_id.doctor_id.user_id.first_name.lower() 
                               or search_booked.lower() in appointment.service_id.doctor_id.user_id.last_name.lower()
                               or search_booked.lower() in appointment.facility_id.street_address.lower() 
                               or search_booked.lower() in appointment.facility_id.postal_code.lower() 
                               or search_booked.lower() in appointment.facility_id.city.lower() 
                               or search_booked.lower() in appointment.facility_id.voivodeship.lower()]
    
    if search_confirmed:
        confirmed_appointments = [appointment for appointment in confirmed_appointments 
                               if search_confirmed.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_confirmed.lower() in appointment.service_id.doctor_id.user_id.first_name.lower() 
                               or search_confirmed.lower() in appointment.service_id.doctor_id.user_id.last_name.lower()
                               or search_confirmed.lower() in appointment.facility_id.street_address.lower() 
                               or search_confirmed.lower() in appointment.facility_id.postal_code.lower() 
                               or search_confirmed.lower() in appointment.facility_id.city.lower() 
                               or search_confirmed.lower() in appointment.facility_id.voivodeship.lower()]

    if search_past:
        past_appointments = [appointment for appointment in past_appointments 
                               if search_past.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_past.lower() in appointment.service_id.doctor_id.user_id.first_name.lower() 
                               or search_past.lower() in appointment.service_id.doctor_id.user_id.last_name.lower()
                               or search_past.lower() in appointment.facility_id.street_address.lower() 
                               or search_past.lower() in appointment.facility_id.postal_code.lower() 
                               or search_past.lower() in appointment.facility_id.city.lower() 
                               or search_past.lower() in appointment.facility_id.voivodeship.lower()]
    
    booked_appointments.sort(key=lambda x: x.appointment_time)
    confirmed_appointments.sort(key=lambda x: x.appointment_time)
    past_appointments.sort(key=lambda x: x.appointment_time)


    # RESERVED
    paginator = Paginator(booked_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        booked_appointments = paginator.page(page)
    except EmptyPage:
        booked_appointments = paginator.page(paginator.num_pages)

    #  CONFIRMED
    paginator = Paginator(confirmed_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        confirmed_appointments = paginator.page(page)
    except EmptyPage:
        confirmed_appointments = paginator.page(paginator.num_pages)

    # PAST
    paginator = Paginator(past_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        past_appointments = paginator.page(page)
    except EmptyPage:
        past_appointments = paginator.page(paginator.num_pages)

    return render(
        request,
        'patient_dashboard.html',
        {
            'past_appointments': past_appointments,
            'booked_appointments': booked_appointments,
            'confirmed_appointments': confirmed_appointments,
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
def change_info_patient_view(request):
    patient = get_object_or_404(Patient, user_id=request.user)

    if request.method == 'POST':
        form = PatientUpdateInfoForm(request.POST)
        if form.is_valid():
            patient.phone_number = form.cleaned_data['phone_number']
            patient.save()
            return redirect('patient_dashboard')
    else:
        form = PatientUpdateInfoForm()

    return render(request, 'phone_number_change.html', {'form': form})

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

def register_patient_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_registered_patient_site.send(sender=user.__class__, user=user, created=True)
            send_welcome_email_patient(user.email, user.username)
            return redirect('home_patient')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/patient/register_patient.html', {'form': form})

class PatientPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Hasło zostało pomyślnie zmienione.')
        return response

    def get_success_url(self):
        return reverse_lazy('patient_dashboard')  

@login_required
def appointment_search_specialization_view(request):
    form =  SpecializationSearchForm(request.GET)
    specializations = Specialization.objects.all()
    city = Facility.city

    if form.is_valid():
        specialization = form.cleaned_data.get('specialization')
        city = form.cleaned_data.get('city')
        if specialization and city:
            return redirect('appointment_search', specialization_id=specialization.id, city=city)

    return render(request, 'appointments_research_specialization.html', {'form': form, 'specializations': specializations, 'city': city})

@login_required
def appointment_search_patient_view(request, specialization_id, city):
    specialization = get_object_or_404(Specialization, id=specialization_id)
    facilities = Facility.objects.filter(city=city)
    services = Service.objects.filter(specialzation_id=specialization)
    doctor = Doctor.objects.filter(service__in=services)

    form = AppointmentSearchForm(request.GET, doctor=doctor, facilities=facilities)
    appointments = []

    if request.method == 'GET' and form.is_valid():
        doctor = form.cleaned_data.get('doctor')
        facility = form.cleaned_data.get('facility')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        time_slot = form.cleaned_data.get('time_slot')
        appointments = Appointment.objects.filter(status='a', service_id__specialzation_id=specialization, appointment_time__gte=timezone.now())

        if doctor:
            appointments = appointments.filter(service_id__doctor_id=doctor)
        if facility:
            appointments = appointments.filter(facility_id=facility)
        if start_date and end_date:
            appointments = appointments.filter(appointment_time__date__range=(start_date, end_date))

        if time_slot == '7-12':
            appointments = appointments.filter(appointment_time__time__gte='07:00', appointment_time__time__lt='12:00')
        elif time_slot == '12-17':
            appointments = appointments.filter(appointment_time__time__gte='12:00', appointment_time__time__lt='17:00')
        elif time_slot == '17-20':
            appointments = appointments.filter(appointment_time__time__gte='17:00', appointment_time__time__lt='20:00')
        elif time_slot == 'all':
            appointments = appointments.filter(appointment_time__time__gte='07:00', appointment_time__time__lt='20:00')

    return render(request, 'appointments_research_results.html', {'form': form, 'appointments': appointments, 'specialization':specialization})

def book_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_booking.html', {'appointment': appointment,})

@transaction.atomic
def complete_book_appointment_view(request, pk):
    new_appointment = get_object_or_404(Appointment, id=pk)

    try:
        patient = request.user.patient
        new_appointment.patient_id = patient
        new_appointment.status = 'b'  
        new_appointment.save()

        existing_appointment = Appointment.objects.filter(
            patient_id=request.user.patient,
            status='b',  
            service_id=new_appointment.service_id,
            appointment_time__gt=new_appointment.appointment_time,
        ).first()

        if existing_appointment:
            existing_appointment.patient_id = None
            existing_appointment.status = 'a'
            existing_appointment.save()

        # ------ mail o rezerwacje wizyty ------
        recipient = request.user.email
        send_email_appointment_confirmation.delay(recipient, new_appointment.id)
        #------------------------------------------
        messages.success(request, 'Rezerwacja zakończona pomyślnie.')
    except Exception as e:
        messages.error(request, f'Błąd podczas rezerwacji: {str(e)}')

    return redirect(reverse('patient_dashboard'))

def cancel_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_cancellation.html', {'appointment': appointment,})

@transaction.atomic
def complete_cancel_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    try:
        appointment.patient_id = None
        appointment.status = 'a'  
        appointment.save()
        send_email_appointment_cancel.delay(request.user.email, appointment.id)
        messages.success(request, 'Anulowano wizytę.')
    except Exception as e:
        messages.error(request, f'Błąd podczas odwływania wizyty: {str(e)}')

    return redirect(reverse('patient_dashboard'))

def confirm_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointment_confirm.html', {'appointment': appointment,})

def complete_confirm_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)

    try:
        appointment.status = 'c'  
        appointment.save()
        messages.success(request, 'Potwierdzanie zakończono pomyślnie.')
    except Exception as e:
        messages.error(request, f'Błąd podczas potwierdzania wizyty: {str(e)}')

    return redirect(reverse('patient_dashboard'))

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
    search_confirmed = request.GET.get('search_confirmed', '')
    # search_past = request.GET.get('search_past', '')

    # Pobieramy wszystkie wizyty lekarza
    all_appointments = (
        Appointment.objects.filter(service_id__doctor_id=doctor)
        .order_by('service_id__specialzation_id','facility_id','appointment_time')
    )

    # Dzielimy wizyty na przeszłe i nadchodzące one od syatusu powinny zależeć a nie od czasu
    # past_appointments = [appointment for appointment in all_appointments if appointment.status == 'd']
    future_appointments = [appointment for appointment in all_appointments if (appointment.appointment_time >= timezone.now() or  (appointment.status == 'c' and appointment.appointment_time < timezone.now()))]

    # Dzielimy nadchodzące wizyty na zarezerwowane i dostępne i potwierdzone
    reserved_appointments = [appointment for appointment in future_appointments if appointment.status == 'b']
    available_appointments = [appointment for appointment in future_appointments if appointment.status == 'a']
    confirmed_appointments = [appointment for appointment in future_appointments if appointment.status == 'c']

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
        
    if search_confirmed:
        confirmed_appointments = [appointment for appointment in confirmed_appointments 
                               if  search_confirmed.lower() in appointment.service_id.specialzation_id.name.lower()
                               or search_confirmed.lower() in appointment.facility_id.street_address.lower() 
                               or search_confirmed.lower() in appointment.facility_id.postal_code.lower() 
                               or search_confirmed.lower() in appointment.facility_id.city.lower() 
                               or search_confirmed.lower() in appointment.facility_id.voivodeship.lower()]

    # if search_past:
    #     past_appointments = [appointment for appointment in past_appointments 
    #                            if search_past.lower() in appointment.service_id.specialzation_id.name.lower()
    #                            or search_past.lower() in appointment.facility_id.street_address.lower() 
    #                            or search_past.lower() in appointment.facility_id.postal_code.lower() 
    #                            or search_past.lower() in appointment.facility_id.city.lower() 
    #                            or search_past.lower() in appointment.facility_id.voivodeship.lower()]
        
    
    available_appointments.sort(key=lambda x: x.appointment_time)
    reserved_appointments.sort(key=lambda x: x.appointment_time)
    confirmed_appointments.sort(key=lambda x: x.appointment_time)
    # past_appointments.sort(key=lambda x: x.appointment_time)
    time_now = timezone.now()

    # AVAILABLE
    paginator = Paginator(available_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        available_appointments = paginator.page(page)
    except EmptyPage:
        available_appointments = paginator.page(paginator.num_pages)
    
    # RESERVED
    paginator = Paginator(reserved_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        reserved_appointments = paginator.page(page)
    except EmptyPage:
        reserved_appointments = paginator.page(paginator.num_pages)

    #  CONFIRMED
    paginator = Paginator(confirmed_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        confirmed_appointments = paginator.page(page)
    except EmptyPage:
        confirmed_appointments = paginator.page(paginator.num_pages)

    return render(
        request,
        'doctor_dashboard.html',
        {
            # 'past_appointments': past_appointments,
            'reserved_appointments': reserved_appointments,
            'available_appointments': available_appointments,
            'confirmed_appointments': confirmed_appointments,
            'time_now': time_now,
        }
    )


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

    search_past = request.GET.get('search_past', '')

    # Pobieramy przeszłe wizyty lekarza
    all_appointments = (
        Appointment.objects.filter(
            service_id__doctor_id=doctor,
        )
        .order_by('service_id__specialzation_id', 'status', 'appointment_time')
        .select_related('patient_id')
    )

    past_appointments = [appointment for appointment in all_appointments if appointment.status == 'd']

    amount = len(past_appointments)
    if search_past:
        past_appointments = [appointment for appointment in past_appointments 
                                if search_past.lower() in appointment.service_id.specialzation_id.name.lower()
                                or search_past.lower() in appointment.facility_id.street_address.lower() 
                                or search_past.lower() in appointment.facility_id.postal_code.lower() 
                                or search_past.lower() in appointment.facility_id.city.lower() 
                                or search_past.lower() in appointment.facility_id.voivodeship.lower()]
    
    past_appointments.sort(key=lambda x: x.appointment_time)

    paginator = Paginator(past_appointments, 4)  # Show 10 appointments per page
    page = request.GET.get('page', 1)
    try:
        past_appointments = paginator.page(page)
    except EmptyPage:
        past_appointments = paginator.page(paginator.num_pages)

    return render(
        request,
        'doctor_past_appointments.html',
        {
            'past_appointments': past_appointments, 'amount': amount,
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
    today = timezone.now().day

    if request.method == 'POST':
        form = AvailabilityForm(request.POST, doctor=doctor)

        if form.is_valid():
            # if form.is_SelectAll:
            #     all_selected = form.select_all_days
            selected_days = [day for day in form.cleaned_data['selected_days']]

            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            duration = form.cleaned_data['duration']
            selected_specialization = form.cleaned_data['specialization']
            selected_facility = form.cleaned_data['facility']

            current_time = start_time

            for selected_date in selected_days:
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
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

    return render(request, template_name, {'form': form, 'today': today})

from datetime import datetime, timedelta

#to nie testowane
def get_dates_for_days(year, month, selected_days):
    first_day_of_month = datetime(year, month, 1)
    current_date = first_day_of_month

    dates_for_selected_days = []

    while current_date.month == month:
        if current_date.weekday() in selected_days:
            dates_for_selected_days.append(current_date)
        current_date += timedelta(days=1)

    return dates_for_selected_days

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

class AppointmentDetailDoctorView(generic.DeleteView):
    model = Appointment
    template_name = 'appointment_detail_doctor.html'
    context_object_name = 'appointment'

# INNE --------------------------------------------------------------------------------------
class FacilityDetailView(generic.DetailView):
    model = Facility
    template_name = 'facility_detail.html'   

class AppointmentDetailView(generic.DetailView):
    model = Appointment
    template_name = 'appointment_detail.html'
    context_object_name = 'appointment'

# MAIL ----------------------------------------------------------------------------------------
def send_welcome_email_patient(recipient_email, username):
    subject = 'Witamy w Promed'
    html_message = render_to_string('email/welcome_email.html', 
                                    {'username': username})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
   
    send_mail(
                subject,
                plain_message,  
                from_email,
                [recipient_email],
                html_message=html_message, 
            )
