from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re


User = get_user_model()


class TextInputWithoutValue(forms.TextInput):
    def format_value(self, value):
        return None


class EmailInputWithoutValue(forms.EmailInput):
    def format_value(self, value):
        return None


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )


class ChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        """Запоминаем пользователя для валидации"""
        super(ChangeForm, self).__init__(*args, **kwargs)
        self.instance = kwargs['instance']

    password = forms.CharField(
        label=("Пароль"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )
    password2 = forms.CharField(
        label=("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        )

    def clean(self):
        """Валидация пароля, почты и ника"""
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        if re.search(r'[^а-яА-ЯёЁ]', first_name):
            raise ValidationError(
                {"first_name": 'Имя должно содержать только русские буквы!'}
            )
        if re.search(r'[^а-яА-ЯёЁ]', last_name):
            raise ValidationError(
                {"last_name": 'Фамилия должна содержать только русские буквы!'}
            )
        if self.instance.username != username:
            UserCreationForm.clean_username(self)
        password1 = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]
        if self.instance.email != email:
            if User.objects.filter(email=self.cleaned_data['email']).exists():
                raise ValidationError(
                    {"email": 'Пользователь с такой почтой уже существует!'}
                )
        if password1 or password2:
            if password1 != password2:
                raise ValidationError(
                    {"password": 'Пароли не совпадают',
                     "password2": 'Пароли не совпадают'}
                )
        else:
            del (self.cleaned_data["password"])
            del (self.cleaned_data["password2"])
        return self.cleaned_data
