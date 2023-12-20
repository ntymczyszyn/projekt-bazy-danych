from django.shortcuts import render
from django.http import HttpResponse

'''
Trzeba zrobić view
- do tworzenia konta?
- do logowana
- do odzyskiwania hasła
PACJENT
- do strony o pacjencie
- class do wyświetlania zarezerwowanych wizyt w terminarzu ? - do strony głównej u Patcjentów
- do przeglądania wizyt (wybór wizyty)
- do rezerwacji wizyty (nie wiem czy to nie będzie to samo co wyżej)
- do anulowania wizyty
- do przeglądania histoii wizyt
LEKARZ
- do strony o lekarzu
- do deklarowania dyspozycji
- do przeglądania wizyt ( to samo co u Pajcentów?, bo tam inne dane osoby będą, więc nie jestem pewna)
- do przeglądania historii wizyt
'''
def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def patient(request):
    return render(request, 'patient_home.html')
#-----------------------------------------------------------------------------------
# wyświetlanie wszystkich wizyt zalogwanego użytownika
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Patient
from django.shortcuts import get_object_or_404

class AppointmentsByUserListView(LoginRequiredMixin, generic.ListView):
    model = Appointment
    template_name = 'promed/appointment_list_user.html' # docelowo będzie _patient
    # paginate_by = 10 # trzeba będzie dodać do base_html  {% block pagination %}

    def get_queryset(self):
        patient = get_object_or_404(Patient, user_id=self.request.user)
        return (
            Appointment.objects.filter(patient_id=patient)
            .order_by('appointment_time')
        )
#-----------------------------------------------------------------------------------   
def visits(request):
    return render(request, 'wizyty.html')

#-----------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------


def reservation(request):
    return render(request, 'rezerwacje.html')