from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('medicine/<int:pk>/', views.add_medicine_review, name='medicine_review'),
    path('doctor/<int:doctor_id>/', views.add_doctor_review, name='doctor_review'),
]