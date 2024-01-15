from django import forms
from .models import Doctor, Facility, Patient, Specialization, CustomUser, Service
from django.contrib.auth.forms import UserCreationForm
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
    

class AppointmentSearchForm(forms.Form):
    TIME_SLOT_CHOICES = [
        ('all', '----------'),
        ('7-12', '7:00 - 12:00'),
        ('12-17', '12:00 - 17:00'),
        ('17-20', '17:00 - 20:00'),
    ]
    #  tu by trzeba było usunąć możliwość wybrania siebie samego
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False, label='Lekarz', widget=forms.Select(attrs={'class':'form-group dropdown bg-info text-light'}))
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), required=False, label='Placówka', widget=forms.Select(attrs={'class':'form-group dropdown bg-info text-light'}))
    # date = forms.DateField(required=False, label='Zakres dni',widget=forms.DateInput( attrs = {'type': 'date', 'class':'form-group dropdown bg-info text-light'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class':'form-group dropdown bg-info text-light'}), label='Od')
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class':'form-group dropdown bg-info text-light'}), label='Do')
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


from datetime import timedelta, datetime
from django.utils import timezone
import logging
import calendar
import locale

logger = logging.getLogger(__name__)
# chciałam dzięki temu zrobić po polsu te daty ale narazie się nie da
# jest chyba w tym jakiś problem z kodowanie UTF-8 - próbowałam to naprawić ale jak narazie na marne
# locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')

# do zrobienia odpowiednich style dla Checkboxów, ale nie działa
from django.utils.safestring import mark_safe

class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if attrs is None:
            attrs = {}
        option_html = super().create_option(name, value, label, selected, index, subindex, attrs)
        html = f'<div class="row">{option_html.strip()}</div>'
        return mark_safe(html.replace('<input', '<div class="col">').replace('type="checkbox"', 'type="checkbox" class="col"'))


class AvailabilityForm(forms.Form):
#     current_year = datetime.now().year
#     select_year = forms.DateField(widget=forms.SelectDateWidget(years=range(current_year, current_year + 1)))
# #  zamienić na wybierz tydzień ?
#     MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]
#     selected_month = forms.ChoiceField(choices=MONTH_CHOICES, label='Wybierz miesiąc')
    selected_days = forms.MultipleChoiceField(
        choices=[], 
        widget=forms.CheckboxSelectMultiple(), 
        label='Wybierz dni')
    
    # selected_date = forms.DateField(widget=forms.SelectDateWidget)

    start_time = forms.TimeField(
        widget=forms.Select(choices=[(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") for hour in range(7, 21) for minute in range(0, 60, 5)],  
                            attrs={'class':'form-group dropdown bg-info text-light'}), 
        label='Czas rozpoczęcia'
    )
    end_time = forms.TimeField(
        widget=forms.Select(choices=[(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") for hour in range(7, 21) for minute in range(0, 60, 5)],  
                            attrs={'class':'form-group dropdown bg-info text-light'}), 
        label='Czas zakończenia'
    )
    specialization = forms.ModelChoiceField(queryset=Specialization.objects.none(), label='Specjalizacja', widget=forms.Select( attrs={'class':'form-group dropdown bg-info text-light'}))
    duration = forms.ChoiceField(choices=[(15, '15 minutes'), (30, '30 minut'), (45, '45 minut'), (60, '60 minut')], label='Czas trwania',  widget=forms.Select( attrs={'class':'form-group dropdown bg-info text-light'}))
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), label='Placówka',  widget=forms.Select( attrs={'class':'form-group dropdown bg-info text-light'}))

    
    
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
        date_range = [today + timedelta(days=x) for x in range(20) if (today + timedelta(days=x)).weekday != 5 or (today + timedelta(days=x)).weekday != 6]
        # self.fields['selected_date'].initial = today
        # choices, names = [((d, d), d.weekday)  for d in date_range]
        # names = [calendar.day_name[day] for day in range(0, 6)]
        # self.fields['selected_days'].widget.attrs.update({'class': 'col'})
        self.fields['selected_days'].choices = [(d, d)  for d in date_range]
        # self.fields['selected_date'].widget.choices = [(d, d) for d in date_range]
        # self.fields['selected_days'].choices = [(str(day), calendar.day_name[day]) for day in range(0, 6)] # till saturday max
        




    def clean_selected_days(self):
            selected_days = self.cleaned_data['selected_days']
            if not selected_days:
                raise forms.ValidationError("Select at least one day.")
            return selected_days


    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        selected_service = cleaned_data.get('service')
        # selected_date = cleaned_data.get('selected_date')

        # if selected_date and selected_date < timezone.now().date():
        #     raise forms.ValidationError("Data nie może być z przeszłości")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Błędnie wybrany przedział czasu")

        if selected_service:
            cleaned_data['duration'] = selected_service.duration
            total_minutes = (end_time.hour - start_time.hour) * 60 + (end_time.minute - start_time.minute)
            if int(cleaned_data['duration']) > int(total_minutes):
                raise forms.ValidationError("Czas trwania usługi przekracza dostępny przedział czasowy")
            
        return cleaned_data

