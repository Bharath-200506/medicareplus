from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/', views.chat_api, name='api'),
    path('suggest-doctors/', views.suggest_doctors, name='suggest_doctors'),
]