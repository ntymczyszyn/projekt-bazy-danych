from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment, Patient

'''
HOME
- do tworzenia konta
- do logowana
- do odzyskiwania hasła
PACJENT
- do przeglądanie odbywanych wizyt (nadchodzących i przeszłych)
- do rezerwacji wizyty
- do anulowania wizyty
LEKARZ
- do deklarowanie dyspozyjności
- do przeglądania wykonywanych wizyt (nadchodzących i przeszłych)
'''
def home(request):
    return render(request, 'home.html')

def login(request): # to do poprawy
    return render(request, 'registration/login.html')

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