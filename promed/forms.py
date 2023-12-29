from django import forms
from .models import Doctor, Facility
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

class AppointmentSearchForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False, label='Lekarz')
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), required=False, label='Placówka')
    
