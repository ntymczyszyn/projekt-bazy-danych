from django.urls import path
from . import views
#zmieniłam bazową ścieżkę na promed!
# więc te tu poniżej są tak jak: promed/home

urlpatterns = [
    path('home', views.home, name="home"),
    path('login', views.login, name="login"),
    path('patient/dashboard',  views.AppointmentsByUserListView.as_view(), name="patient-dashboard"),
    path('patient/details', views.PatientDetailView.as_view(), name='patient-detail'),
    path('visits', views.visits, name="visits"),
    path("reservations", views.reservation, name="reservations")
]