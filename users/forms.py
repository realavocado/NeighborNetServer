from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'bio', 'address', 'image_url')


class CustomUserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('email', 'password')
