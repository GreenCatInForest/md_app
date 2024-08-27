from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'name', 'surname', 'password1', 'password2']

class UserLoginForm(forms.Form):
    model = User
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)