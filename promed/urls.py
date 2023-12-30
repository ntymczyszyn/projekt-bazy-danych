from django.urls import path, include
from . import views
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/promed/home/', permanent=True)),
    path('home/', views.home, name="home"),
]

urlpatterns += [
    path('patient/dashboard', views.appointments_by_user_list, name="patient_dashboard"),
    path('patient/details', views.patient_detail, name='patient_detail'),
    path('patient/search/appointments/', views.appointment_search, name='appointment_search'),
    path('pateint/info/complete', views.complete_patient_info, name='complete_patient_info'),
]

urlpatterns += [
    path('doctor/dashboard',  views.AppointmentsByDoctorListView.as_view(), name="doctor_dashboard"),
    path('doctor/details', views.doctor_detail_view, name='doctor_detail'),
]

# Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/patient/login/', views.PatientLoginView.as_view(), name='patient_login'),
    path('accounts/patient/login/denied', views.patient_access_denied, name='patient_access_denied'),
    path('accounts/patient/register/', views.register_user, name='patient_register'),
    path('accounts/', include('django.contrib.auth.urls')),
    
]
# path('accounts/logout/', CustomLogoutView.as_view(), name='custom_logout'),
# path('accounts/password_change/', CustomPasswordChangeView.as_view(), name='custom_password_change'),
# path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='custom_password_reset'),
# path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='custom_password_reset_confirm'),

urlpatterns += [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('facility/<int:pk>/', views.FacilityDetailView.as_view(), name='facility_detail'),
    path('appointment/<uuid:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointment/<uuid:pk>/confirm', views.confirm_appointment_view, name='confirm_appointment'),
    path('appointment/<uuid:pk>/complete', views.complete_appointment_view, name='complete_appointment_booking'),
]
