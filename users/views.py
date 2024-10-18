from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm, PasswordResetRequestForm, CustomPasswordResetForm
from core.models import User, PasswordReset
from users.forms import CustomPasswordResetForm
from django.contrib.auth import get_user_model

from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

# for password reset

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import ResetPasswordRequestSerializer, ResetPasswordSerializer

from django.contrib.auth.tokens import default_token_generator
from .forms import CustomPasswordResetForm  


import os



def user_login_register(request):
    user_login_form = UserLoginForm()
    user_register_form = UserRegisterForm()
    register_active = False  # By default, show the login form

    if request.method == 'POST':
        # Determine which form is being submitted
        if 'register' in request.POST:
            print('POST Register request detected')
            user_register_form = UserRegisterForm(request.POST)  # Bind registration form with POST data
            user_login_form = UserLoginForm()  # Initialize an empty login form

            if user_register_form.is_valid():
                print('User register form is valid')
                user = user_register_form.save(commit=False)
                user.set_password(user_register_form.cleaned_data['password1'])  # Hash the password
                user.save()  # Save the user to the database
                messages.success(request, 'Your account has been created! You will be now logged in.')
                login(request, user)  # Log in the user
                return redirect('report')  # Redirect to user account page
            else:
                print(f"Register form errors: {user_register_form.errors}")  # Debugging statement
                register_active = True  # Keep the register form active

        elif 'login' in request.POST:
            print('POST Login request detected')
            user_login_form = UserLoginForm(request.POST)  # Bind login form with POST data
            remember_me = user_login_form.cleaned_data.get('remember_me')

            if user_login_form.is_valid():
                email = user_login_form.cleaned_data.get('email')
                password = user_login_form.cleaned_data.get('password')

                # Check if the email exists before authenticating
                if not User.objects.filter(email=email).exists():
                    user_login_form.add_error('email', 'No account found with this email.')
                else:
                    print(f"Attempting to authenticate user with email: {email} and password: {password}")
                    user = authenticate(request, email=email, password=password)
                    print(f"Authentication result: {user}")

                    if user is not None:
                        login(request, user)
                        print(f"User {user.email} logged in. Session key: {request.session.session_key}")
                        if remember_me:
                        # Set session to expire in 30 days
                            request.session.set_expiry(60 * 60 * 24 * 30)
                        else:
                            # Set session to expire when the browser is closed
                            request.session.set_expiry(0)
                        messages.success(request, 'You have successfully logged in!')
                        return redirect('report')
                        
                    else:
                        messages.error(request, 'Invalid email or password')
                        print("Invalid email or password")
                        
            else:
                print(f"Login form errors: {user_login_form.errors}")
                
    else:
        user_login_form = UserLoginForm()
        user_register_form = UserRegisterForm()

    return render(request, 'users/login-register.html', {
        'user_login_form': user_login_form,
        'user_register_form': user_register_form,
        'register_active': register_active,  # Pass the active form status
    })


def user_logout(request):
    print('User is logging out')
    logout(request)
    return redirect('login_register')

# Customise the password-reset views to account for "already logged in" users trying to reset their password.
class LogoutIfAuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
    
# Implement the password reset behaviour customisation
    
class CustomPasswordResetView(LogoutIfAuthenticatedMixin, PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_message = ("We've emailed you instructions for setting your password, "
                       "if an account exists with the email you entered. You should receive them shortly. "
                       "If you don't receive an email, "
                       "please make sure you've entered the address you registered with, and check your spam folder.")
    success_url = reverse_lazy('password_reset_done')  # Use reverse_lazy for URLs

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = get_user_model().objects.filter(email=email).first()
        if user:
            self.send_mail(form, user)
        return super().form_valid(form)

    def send_mail(self, form, user):
        context = {
            "email": user.email,
            "domain": self.request.META["HTTP_HOST"],
            "site_name": "Your Website",
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": default_token_generator.make_token(user),
            "protocol": "http",  # Change to 'https' if using HTTPS
        }
        subject = render_to_string(self.subject_template_name, context)
        subject = "".join(subject.splitlines())
        email_content = render_to_string(self.email_template_name, context)
        send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])

class CustomPasswordResetDoneView(LogoutIfAuthenticatedMixin, PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(LogoutIfAuthenticatedMixin, PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

# class CustomPasswordResetCompleteView(LogoutIfAuthenticatedMixin, PasswordResetCompleteView):
#     template_name = 'registration/password_reset_complete.html'

class CustomPasswordResetCompleteView(LogoutIfAuthenticatedMixin, PasswordResetCompleteView):pass