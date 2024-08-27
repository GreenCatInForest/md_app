from django.urls import path
from django.contrib.auth import views as auth_views
from .views import password_reset_request_view, password_reset_confirm_view
from . import views

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('logout_page/', views.user_logout, name='logout_page'),
    path('password-reset/', password_reset_request_view, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]