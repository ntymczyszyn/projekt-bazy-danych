from django.urls import path
from . import views
# zmieniłam bazową ścieżkę na promed!
# więc te tu poniżej są tak jak: promed/home

urlpatterns = [
    path('home/', views.home, name="home"),
    path('login/', views.login, name="login"),
    path("reservations", views.reservation, name="reservations") # to do zmiany
]

# ścieżki do strony pacjenta
urlpatterns += [
    path('patient/dashboard',  views.AppointmentsByUserListView.as_view(), name="patient-dashboard"),
    path('patient/details', views.PatientDetailView.as_view(), name='patient-detail'),
]

# ścieżki do strony lekarza
urlpatterns += [
    path('doctor/dashboard',  views.AppointmentsByDoctorListView.as_view(), name="doctor-dashboard"),
    path('doctor/details', views.DoctorDetailView.as_view(), name='doctor-detail'),
]