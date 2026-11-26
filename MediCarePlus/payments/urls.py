from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate'),
    path('appointment/<int:appointment_id>/', views.initiate_appointment_payment, name='initiate_appointment'),
    path('callback/', views.payment_callback, name='callback'),
]