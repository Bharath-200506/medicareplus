from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    path('upload/', views.upload_prescription, name='upload'),
    path('my/', views.prescription_list, name='list'),
    path('review/', views.review_prescriptions, name='review'),
    path('<int:pk>/approve/', views.approve_prescription, name='approve'),
    path('<int:pk>/reject/', views.reject_prescription, name='reject'),
]