from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path('', views.home, name="home"),
    path('login', views.login, name="login"),
    path('patient', views.patient, name="patient"),
    path('visits', views.visits, name="visits"),

    path('visits/', views.VisitsListView.as_view(), name='visits-view'),
    path('patient-detail/', views.PatientDetailView.as_view(), name='patient-detail'),

    path("reservations", views.reservation, name="reservations")
]