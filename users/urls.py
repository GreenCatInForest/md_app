from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
   
    path('logout/', views.user_logout, name='logout'),
    path('logout_page/', views.user_logout, name='logout_page'),
    path('login_register/', views.user_login_register, name='login_register'),
    ]