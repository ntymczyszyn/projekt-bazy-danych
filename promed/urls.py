from django.urls import path, include
from . import views
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/promed/home/', permanent=True)),
    path('home/', views.home_view, name="home"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)), # tylko na stronie głownej się wyświetla
    ]

urlpatterns += [
    path('home/pateint', views.home_patient_view, name="home_patient"),
    path('patient/dashboard', views.patient_dashboard_view, name="patient_dashboard"),
    path('patient/details', views.patient_detail_view, name='patient_detail'),
    path('patient/search/appointments/specialization', views.appointment_search_specialization_view, name='appointment_search_specialization'),
    path('patient/search/appointments/<int:specialization_id><str:city>/', views.appointment_search_patient_view, name='appointment_search'),
    path('pateint/info/complete', views.complete_info_patient_view, name='complete_patient_info'),
    path('patient/appointment/<uuid:pk>/detail', views.cancel_appointment_view, name='detail_cancel_appointment'),
    path('patient/appointment/<uuid:pk>/cancel/complete', views.complete_cancel_appointment_view, name='complete_appointment_cancellation'),
    # Do potwierdzania wizyty przez pacjenta
    path('patient/appointment/<uuid:pk>/confirm', views.confirm_appointment_view, name='confirm_appointment'),
    path('patient/appointment/<uuid:pk>/confirm/complete', views.complete_confirm_appointment_view, name='complete_confirm_appointment'),
    path('patient/password-change/', views.PatientPasswordChangeView.as_view(), name='patient_password_change'),
    path('patient/phone-number-change/', views.change_info_patient_view, name='patient_change_phone_number'),
    
]

urlpatterns += [
    path('home/staff', views.home_staff_view, name="home_doctor"),
    path('doctor/dashboard',  views.doctor_dashboard_view, name="doctor_dashboard"),
    path('doctor/details', views.doctor_detail_view, name='doctor_detail'),
    path('doctor/past-appointments/', views.doctor_past_appointments_view, name='doctor_past_appointments'),
    path('doctor/availability/', views.doctor_availability, name='doctor_availability'),
    path('doctor/password-change/', views.DoctorPasswordChangeView.as_view(), name='doctor_password_change'),
    path('doctor/appointment/<uuid:pk>/confirm', views.confirm_appointment_doctor_view, name='confirm_appointment_doctor'),
    path('doctor/appointment/<uuid:pk>/confirm/complete', views.confirm_appointment_doctor_done_view, name='complete_appointment_confirmation'),
    path('doctor/phone-number-change/', views.change_info_doctor_view, name='doctor_change_phone_number'),
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
    path('accounts/logout/', views.MyLogoutView.as_view(), name='logout'), # magdzie pomogło  wylogowywaniem się
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
    path('appointment/<uuid:pk>/doctor', views.AppointmentDetailDoctorView.as_view(), name='appointment_detail_doctor'),
    path('appointment/<uuid:pk>/book/confirm', views.book_appointment_view, name='book_appointment'),
    path('appointment/<uuid:pk>/book/complete', views.complete_book_appointment_view, name='complete_appointment_booking'),
]
