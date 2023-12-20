# forms.py

from django import forms
from .models import Doctor, Facility

class AppointmentSearchForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False, label='Lekarz')
    facility = forms.ModelChoiceField(queryset=Facility.objects.all(), required=False, label='Placówka')
    
