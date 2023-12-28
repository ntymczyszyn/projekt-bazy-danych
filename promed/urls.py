from django.urls import path, include
from . import views
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/promed/home/', permanent=True)),
    path('home/', views.home, name="home"),
]

# ścieżki do strony pacjenta
urlpatterns += [
    path('patient/dashboard', views.AppointmentsByUserListView.as_view(), name="patient_dashboard"),
    path('patient/details', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patient/reservation', views.ReservationAppointmentsView.as_view(), name='patient_reservation'),
    path('patient/search/appointments/', views.AppointmentSearchView.as_view(), name='appointment_search'),
]

# ścieżki do strony lekarza
urlpatterns += [
    path('doctor/dashboard',  views.AppointmentsByDoctorListView.as_view(), name="doctor_dashboard"),
    path('doctor/details', views.DoctorDetailView.as_view(), name='doctor_detail'),
]

# Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/patient/login/', views.PatientLoginView.as_view(), name='patient_login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
# path('accounts/logout/', CustomLogoutView.as_view(), name='custom_logout'),
# path('accounts/password_change/', CustomPasswordChangeView.as_view(), name='custom_password_change'),
# path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='custom_password_reset'),
# path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='custom_password_reset_confirm'),

urlpatterns += [
    path('accounts/patient/login/denied', views.pateint_access_denied, name='patient_access_denied'),
]