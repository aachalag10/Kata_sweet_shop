# sweet_shop/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('order/<int:sweet_id>/', views.place_order, name='place_order'),
    path('orders/', views.view_orders, name='view_orders'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='sweet_shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
