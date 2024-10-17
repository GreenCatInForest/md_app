from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
   
    path('logout/', views.user_logout, name='logout'),
    path('logout_page/', views.user_logout, name='logout_page'),
    path('login_register/', views.user_login_register, name='login_register'),
    # path('accounts/login/', views.user_login_register, name='login_register'),
    # path('password-forgot/', views.CustomPasswordResetView.as_view(), name='password-forgot'),
       # Use your custom password reset views instead of auth_views
    path('password-forgot/',
         views.CustomPasswordResetView.as_view(),
         name='password-forgot'),
    path('password-reset/done/',
         views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]