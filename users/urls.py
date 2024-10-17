from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
   
    path('logout/', views.user_logout, name='logout'),
    path('logout_page/', views.user_logout, name='logout_page'),
    path('login_register/', views.user_login_register, name='login_register'),
    # path('accounts/login/', views.user_login_register, name='login_register'),
    # path('password-forgot/', views.CustomPasswordResetView.as_view(), name='password-forgot'),
    path('password_reset_form/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'
         ),
         name='password_reset_form'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
 
    
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]