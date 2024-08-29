from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, TextInput
from core.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'name', 'surname', 'password1', 'password2']


class UserLoginForm(forms.Form):
    model = User
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'w-full h-12 py-3 mx-2 bg-gray-50 border border-gray-300 text-gray-900 text-sm font-semibold rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter your email',
                'id': 'email',
                'required': True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm font-semibold rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
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