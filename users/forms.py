from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, TextInput, PasswordInput
from core.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    model = User
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Email',
                'id': 'email',
                'required': True,
            }
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Name',
                'id': 'name',
                'required': True,
            }
        )
    )
    surname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Surname',
                'id': 'surname',
                'required': True,
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Password',
                'id': 'password1',
                'required': True,
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Confirm your password',
                'id': 'password2',
                'required': True,
            }
        )
    )

    



class UserLoginForm(forms.Form):
    model = User
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Enter your email',
                'id': 'email',
                'required': True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'input-field',
                'placeholder': 'Enter your password',
                'id': 'password',
                'required': True,
            }
        )
    )
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password")
            if not user.is_active:
                raise ValidationError("This account is inactive.")
        return cleaned_data
  
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)