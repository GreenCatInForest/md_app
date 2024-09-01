from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField, TextInput, PasswordInput
from core.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
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
    class Meta:
        model = User  # Use your custom User model
        fields = ['email', 'name', 'surname', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                # If the field has errors, add 'error' class to the field's widget
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = existing_classes + ' error'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', 'An account with this email already exists')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match')
        return cleaned_data
 


class UserLoginForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                # If the field has errors, add 'error' class to the field's widget
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = existing_classes + ' error'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            # Check if a user with the provided email exists
            if not User.objects.filter(email=email).exists():
                self.add_error('email', 'No account found with this email')
            else:
                user = authenticate(email=email, password=password)
                if user is None:
                    # If authentication fails, it means the password is incorrect
                    self.add_error('password', 'Incorrect password')
                elif not user.is_active:
                    # If the user is inactive
                    raise ValidationError("This account is inactive.")
        return cleaned_data
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)