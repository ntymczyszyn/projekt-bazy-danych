from django.urls import path, include
from . import views
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/promed/home/', permanent=True)),
    path('home/', views.home_view, name="home"),
]

urlpatterns += [
    path('home/pateint', views.home_patient_view, name="home_patient"),
    path('patient/dashboard', views.patient_dashboard_view, name="patient_dashboard"),
    path('patient/details', views.patient_detail_view, name='patient_detail'),
    path('patient/search/appointments/', views.appointment_search_patient_view, name='appointment_search'),
    path('pateint/info/complete', views.complete_info_patient_view, name='complete_patient_info'),
    path('patient/appointment/<uuid:pk>/detail', views.cancel_appointment_view, name='detail_cancel_appointment'),
    path('patient/appointment/<uuid:pk>/cancel/complete', views.confirm_cancel_appointment_view, name='complete_appointment_cancellation'),
    path('patient/password-change/', views.PatientPasswordChangeView.as_view(), name='patient_password_change'),
]

urlpatterns += [
    path('home/doctor', views.home_doctor_view, name="home_doctor"),
    path('doctor/dashboard',  views.doctor_dashboard_view, name="doctor_dashboard"),
    path('doctor/details', views.doctor_detail_view, name='doctor_detail'),
    path('doctor/past-appointments/', views.doctor_past_appointments_view, name='doctor_past_appointments'),
    # path('doctor/availability/', views.doctor_availability, name='doctor_availability'),
    path('doctor/password-change/', views.DoctorPasswordChangeView.as_view(), name='doctor_password_change'),
]

# Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/patient/login/', views.PatientLoginView.as_view(), name='patient_login'),
    path('accounts/patient/login/denied', views.patient_access_denied_view, name='patient_access_denied'),
    path('accounts/patient/register/', views.register_patient_view, name='patient_register'),
    path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += [
    path('accounts/doctor/login/', views.DoctorLoginView.as_view(), name='doctor_login'),
    path('accounts/doctor/login/denied', views.doctor_access_denied_view, name='doctor_access_denied'),
    path('accounts/logout/', views.custom_logout, name='custom_logout'),
    path('accounts/logout/', views.MyLogoutView.as_view(), name='logout'),
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
    path('appointment/<uuid:pk>/book/confirm', views.confirm_appointment_view, name='confirm_appointment'),
    path('appointment/<uuid:pk>/book/complete', views.complete_appointment_view, name='complete_appointment_booking'),
]
