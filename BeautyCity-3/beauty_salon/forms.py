from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import UserProfile


class RegisterUser(UserCreationForm):
    email = forms.EmailField(
        max_length=254, 
        help_text="Обязательное поле. Введите действующий email."
    )
    phone = forms.CharField(
        max_length=15, 
        required=False, 
        help_text="Необязательное поле."
    )

    class Meta:
        model = UserProfile
        fields = ("username", "email", "phone", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)