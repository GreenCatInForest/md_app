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

from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm, PasswordResetRequestForm
from core.models import User, PasswordReset
from django.contrib.auth import get_user_model

# for password reset

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import ResetPasswordRequestSerializer, ResetPasswordSerializer

import os


def user_register(request):
    if request.method == 'POST': 
        user_register_form = UserRegisterForm(request.POST) # Create a new user form
        if user_register_form.is_valid(): # Check if the form is valid
            user = user_register_form.save(commit=False) # Create a new user object but avoid saving it yet
            user.set_password(user_register_form.cleaned_data['password1']) # Hash the password
            user.save()  # Save the user to the database
            messages.success(request, 'Your account has been created! You will be now log in.')
            login(request, user)  # Log in the user
            # return HttpResponse('Hello '+user.name+' '+user.surname + ' You have successfully registered!')
            return redirect('report')  # Redirect to user account page
    else:
        user_register_form = UserRegisterForm() # Create a new user form
    return render(request, 'users/register.html', {'user_register_form': user_register_form}) 

def user_login(request):
    if request.method == 'POST': 
        user_login_form = UserLoginForm(request.POST)
        if user_login_form.is_valid():
            email = user_login_form.cleaned_data.get('email')
            password = user_login_form.cleaned_data.get('password')
            print(f"Attempting to authenticate user with email: {email} and password: {password}")
            user = authenticate(request, email=email, password=password)
            print(f"Authentication result: {user}")
            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in!')
                return redirect('report')
            else:
                messages.error(request, 'Invalid email or password')
                print("Invalid email or password")
    else:
        user_login_form = UserLoginForm()
    
    return render(request, 'users/login.html', {'user_login_form': user_login_form})


def user_logout(request):
    print('User is logging out')
    logout(request)
    return redirect('register')

def password_reset_request_view(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                subject = "Password Reset Requested"
                email_template_name = "password/password_reset_email.txt"
                context = {
                    "email": user.email,
                    "domain": request.META["HTTP_HOST"],
                    "site_name": "Your Website",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "http",
                }
                email_message = render_to_string(email_template_name, context)
                send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [user.email])
                messages.success(request, "A link to reset your password has been sent to your email.")
                return redirect("login")
            else:
                messages.error(request, "No account found with that email address.")
    else:
        form = PasswordResetRequestForm()
    return render(request, "password/password_reset_form.html", {"form": form})

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, "password/password_reset_confirm.html")
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("password_reset_request")
    
