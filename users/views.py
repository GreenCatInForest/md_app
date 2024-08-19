from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm
from core.models import User, PasswordReset

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
            return redirect('report-request')  # Redirect to user account page
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
                return redirect('report-request')
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

# password forgot 1 implementation

# class RequestPasswordReset(generics.GenericAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = ResetPasswordRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         email = request.data['email']
#         user = User.objects.filter(email__iexact=email).first()

#         if user:
#             token_generator = PasswordResetTokenGenerator()
#             token = token_generator.make_token(user) 
#             reset = PasswordReset(email=email, token=token)
#             reset.save()

#             reset_url = f"{os.environ['PASSWORD_RESET_BASE_URL']}/{token}"

#             # Sending reset link via email (commented out for clarity)
#             # ... (email sending code)

#             return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)

# class ResetPassword(generics.GenericAPIView):
#     serializer_class = ResetPasswordSerializer, 
#     permission_classes = []

#     def post(self, request, token):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
        
#         new_password = data['new_password']
#         confirm_password = data['confirm_password']
        
#         if new_password != confirm_password:
#             return Response({"error": "Passwords do not match"}, status=400)
        
#         reset_obj = PasswordReset.objects.filter(token=token).first()
        
#         if not reset_obj:
#             return Response({'error':'Invalid token'}, status=400)
        
#         user = User.objects.filter(email=reset_obj.email).first()
        
#         if user:
#             user.set_password(request.data['new_password'])
#             user.save()
            
#             reset_obj.delete()
            
#             return Response({'success':'Password updated'})
#         else: 
#             return Response({'error':'No user found'}, status=404)
        
# password forgot 2 implementation

def password_forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Handle invalid email
            return render(request, 'users/password_forgot.html', {'error': 'Invalid email'})

        # Generate token and send reset email
        token = default_token_generator.make_token(user)
        print('here is the token '+ token)
        reset_link = request.build_absolute_uri(f'/reset-password/{token}/')
        send_mail(
            'Password Reset',
            f'Click the link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return render(request, 'users/password_forgot.html', {'message': 'Password reset email sent'})
    return render(request, 'users/password_forgot.html')

def password_reset(request, token):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        # Validate token and set new password
        try:
            user = User.objects.get(email=request.POST.get('email'))
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return redirect('login')  # Redirect to login page after password reset
            else:
                # Invalid token
                return render(request, 'users/password_reset', {'error': 'Invalid token'})
        except User.DoesNotExist:
            # Handle invalid email
            return render(request, 'users/password_reset.html', {'error': 'Invalid email'})
    return render(request, 'users/password_reset.html', {'token': token})


