from django import forms
from .models import Doctor, Facility, Patient, Specialization, CustomUser
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.core.exceptions import ValidationError   
from django.core.validators import MaxValueValidator
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

class AppointmentSearchForm(forms.Form):
    specialization = forms.ModelChoiceField(queryset=Specialization.objects.all(), required=True, label='Specjalizacja')
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False, label='Lekarz')
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), required=False, label='Placówka')
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

class PatientInfoForm(forms.Form):
    phone_number = forms.CharField(max_length=10, label='Numer telefonu')
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
