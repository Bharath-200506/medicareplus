from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:pk>/', views.add_to_cart, name='add'),
    path('remove/<int:pk>/', views.remove_from_cart, name='remove'),
    path('update/<int:pk>/', views.update_cart, name='update'),
    path('save-for-later/<int:pk>/', views.save_for_later, name='save_for_later'),
    path('move-to-cart/<int:pk>/', views.move_to_cart, name='move_to_cart'),
]