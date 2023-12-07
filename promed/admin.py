from django.contrib import admin
from .models import Facility

admin.site.site_header = "Promed administration"

admin.site.register(Facility)