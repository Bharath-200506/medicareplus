from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book'),
    path('my/', views.appointment_list, name='list'),
    path('doctor/', views.doctor_appointments, name='doctor_appointments'),
    path('<int:pk>/approve/', views.approve_appointment, name='approve'),
    path('<int:pk>/reject/', views.reject_appointment, name='reject'),
    path('<int:pk>/complete/', views.complete_appointment, name='complete'),
    path('<int:pk>/message/', views.send_patient_message, name='send_patient_message'),
]