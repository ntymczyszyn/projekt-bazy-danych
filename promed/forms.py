from django import forms
from .models import Doctor, Facility, Patient, Specialization, CustomUser, Service
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.core.exceptions import ValidationError   
from django.core.validators import MaxValueValidator
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Imię')
    last_name = forms.CharField(max_length=30, required=True, label='Nazwisko')
    email = forms.EmailField(max_length=254, required=True, label='Email')

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

class SpecializationSearchForm(forms.Form):
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(), 
        required=True, label='Specjalizacja', 
        widget=forms.Select(attrs={'class':'form-group dropdown bg-info text-light'}))
    
# ---------------- To jest do zablokowania sobót i niedziel w wyborze terminów -------------
#  ale na razie nie działa - można usunąć
from django.forms import DateInput
from django.utils.safestring import mark_safe

class DisabledWeekendsDateInput(DateInput):
    class Media:
        css = {
            'all': ("https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css", 
                    "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css",
                    "https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.10.0/css/pikaday.min.css",)
        }
        js = (  "https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.10.0/pikaday.min.js",
                "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js",
                "https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.slim.min.js",
                "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.slim.min.js",
                "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
                "https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js",
            )
        
    def render(self, name, value, attrs=None, renderer=None):
        js = '''
            <script>
                document.addEventListener('DOMContentLoaded', function () {
                    const dateInput = document.getElementById('id_date');
                    const picker = new Pikaday({
                        field: dateInput,
                        format: 'YYYY-MM-DD',
                        onSelect: function () {
                            const selectedDate = new Date(picker.getDate());
                            if (selectedDate.getDay() === 0 || selectedDate.getDay() === 6) {
                                picker.setDate(null);
                                alert('Please select a weekday.');
                            }
                        },
                        toString: function (date, format) {
                            if (!date) return '';
                            const day = date.getDate();
                            const month = date.getMonth() + 1;
                            const year = date.getFullYear();
                            return year + '-' + (month < 10 ? '0' : '') + month + '-' + (day < 10 ? '0' : '') + day;
                        },
                        firstDay: 1, // Start the week on Monday
                        minDate: new Date(), // Disallow dates before today
                        maxDate: new Date(2025, 11, 31), // Disallow dates after 2025-12-31
                        disableWeekends: true, // Disable weekends
                    });
                });
            </script>
        ''' % {'id': attrs['id']}
        attrs = {'type': 'date' } #,'class':'bg-info text-light'}
        rendered = super().render(name, value, attrs, renderer)
        return mark_safe(rendered + js)
    

# ------------------------------------------------------------------------------------------
#  Nie umiem tego zrobić w ten sposób :((

class AppointmentSearchForm(forms.Form):
    TIME_SLOT_CHOICES = [
        ('all', '----------'),
        ('7-12', '7:00 - 12:00'),
        ('12-17', '12:00 - 17:00'),
        ('17-20', '17:00 - 20:00'),
    ]
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False, label='Lekarz', widget=forms.Select(attrs={'class':'form-group dropdown bg-info text-light'}))
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), required=False, label='Placówka', widget=forms.Select(attrs={'class':'form-group dropdown bg-info text-light'}))
    date = forms.DateField(required=False, label='Zakres dni',widget=forms.DateInput( attrs = {'type': 'date', 'class':'form-group dropdown bg-info text-light'}))
    time_slot = forms.ChoiceField(choices=TIME_SLOT_CHOICES, required=False, label='Przedział czasowy',  widget=forms.Select( attrs={'class':'form-group dropdown bg-info text-light'}))
    
    def __init__(self, *args, **kwargs):
            doctor = kwargs.pop('doctor', None)
            super(AppointmentSearchForm, self).__init__(*args, **kwargs)

            if doctor:
                self.fields['doctor'].queryset = doctor

class PatientInfoForm(forms.Form):
    phone_number = forms.CharField(max_length=9, label='Numer telefonu')
    date_of_birth = forms.DateField(
        label='Data urodzenia',
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[MaxValueValidator(limit_value=date.today())],
    )
    pesel = forms.CharField(max_length=11, label='PESEL')

    def clean_pesel(self):
        pesel = self.cleaned_data.get('pesel')

        if len(pesel) != 11:
            raise ValidationError('PESEL powinien mieć 11 cyfr.')

        if not pesel.isdigit():
            raise ValidationError('PESEL powinien składać się z samych cyfr.')

        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]
        checksum = sum(int(p) * w for p, w in zip(pesel, weights)) % 10
        if checksum != 0 or Patient.objects.filter(pesel=pesel).exists():
            raise ValidationError('Nieprawidłowy PESEL.')

        return pesel


from datetime import timedelta
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

class AvailabilityForm(forms.Form):
    selected_date = forms.DateField(widget=forms.SelectDateWidget, label='Wybrany dzień')
    start_time = forms.TimeField(
        widget=forms.Select(choices=[(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") for hour in range(7, 21) for minute in range(0, 60, 5)]), label='Czas rozpoczęcia'
    )
    end_time = forms.TimeField(
        widget=forms.Select(choices=[(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") for hour in range(7, 21) for minute in range(0, 60, 5)]), label='Czas zakończenia'
    )
    specialization = forms.ModelChoiceField(queryset=Specialization.objects.none(), label='Specjalizacja')
    duration = forms.ChoiceField(choices=[(15, '15 minutes'), (30, '30 minut'), (45, '45 minut'), (60, '60 minut')], label='Czas trwania')
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), label='Placówka')

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        available_specializations = Specialization.objects.filter(service__doctor_id=doctor)
        available_facilities = Facility.objects.all()
        super(AvailabilityForm, self).__init__(*args, **kwargs)

        self.fields['specialization'].queryset = available_specializations
        self.fields['facility'].queryset = available_facilities
        # ten zakres miesiąca do przodu mi coś nie działa 
        today = timezone.now().date()
        four_weeks_later = today + timedelta(weeks=4)
        date_range = [today + timedelta(days=x) for x in range((four_weeks_later - today).days)]
        self.fields['selected_date'].initial = today
        self.fields['selected_date'].widget.choices = [(d, d) for d in date_range]

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        selected_service = cleaned_data.get('service')
        selected_date = cleaned_data.get('selected_date')

        if selected_date and selected_date < timezone.now().date():
            raise forms.ValidationError("Data nie może być z przeszłości")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Błędnie wybrany przedział czasu")

        if selected_service:
            cleaned_data['duration'] = selected_service.duration
            total_minutes = (end_time.hour - start_time.hour) * 60 + (end_time.minute - start_time.minute)
            if int(cleaned_data['duration']) > int(total_minutes):
                raise forms.ValidationError("Czas trwania usługi przekracza dostępny przedział czasowy")
            

        return cleaned_data

