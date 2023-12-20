from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name="home"),
]

# ścieżki do strony pacjenta
urlpatterns += [
    path('patient/dashboard', views.AppointmentsByUserListView.as_view(), name="patient-dashboard"),
    path('patient/details', views.PatientDetailView.as_view(), name='patient-detail'),
    path('patient/reservation', views.ReservationAppointmentsView.as_view(), name='patient-reservation'),
    path('patient/search/appointments/', views.AppointmentSearchView.as_view(), name='appointment-search'),
]

# ścieżki do strony lekarza
urlpatterns += [
    path('doctor/dashboard',  views.AppointmentsByDoctorListView.as_view(), name="doctor-dashboard"),
    path('doctor/details', views.DoctorDetailView.as_view(), name='doctor-detail'),
]
