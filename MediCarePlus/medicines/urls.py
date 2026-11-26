from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    path('', views.home, name='home'),
    path('medicines/', views.medicine_list, name='list'),
    path('medicines/add/', views.add_medicine, name='add_medicine'),
    path('medicines/<int:pk>/', views.medicine_detail, name='detail'),
    path('medicines/wishlist/', views.wishlist_view, name='wishlist'),
    path('medicines/wishlist/<int:pk>/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
]