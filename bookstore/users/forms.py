from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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
        fields = self.cleaned_data.copy()
        for field in fields:
            if not fields[field]:
                del (self.cleaned_data[field])
            elif (hasattr(self.instance, field) and
                    eval('self.instance.' + field) == fields[field]):
                del (self.cleaned_data[field])
        UserCreationForm.clean_username(self)
        password1 = self.cleaned_data.get("password", False)
        password2 = self.cleaned_data.get("password2", False)
        if password1 or password2:
            if password1 is False:
                raise ValidationError(
                    {"password": 'Введите пароль!'}
                )
            elif password2 is False:
                raise ValidationError(
                    {"password2": 'Введите подтверждение пароля!'}
                )
            elif password1 != password2:
                raise ValidationError(
                    {"password": 'Пароли не совпадают',
                     "password2": 'Пароли не совпадают'}
                )
        return self.cleaned_data
