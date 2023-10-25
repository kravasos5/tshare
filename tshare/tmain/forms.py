from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .apps import user_registered
from .models import User, Transport


class ChangeUserInfoForm(forms.ModelForm):
    '''Форма пользовательских данных'''
    email = forms.EmailField(required=True,
                             label='Адрес электронной почты')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'send_messages', 'latitude', 'longitude',
                  'radius', 'balance')

class RegisterUserForm(forms.ModelForm):
    '''форма для регистрации пользователя'''
    email = forms.EmailField(required=True,
                             label='Адрес электронный почты')
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Введите пароль повторно',
                                widget=forms.PasswordInput)
    captcha = CaptchaField(label='Каптча')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введённые пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_messages')

class DeleteUserForm(forms.Form):
    '''форма для удаления пользователя'''
    username = forms.CharField(required=True, label='Логин')
    password = forms.CharField(required=True, label='Пароль',
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    class Meta:
        fields = ('username', 'password')

class UserTransportForm(forms.ModelForm):
    '''Форма изменения/добавления ТС'''
    class Meta:
        model = Transport
        fields = ('transport_type', 'model', 'color', 'identifier',
                  'description', 'latitude', 'longitude',
                  'hour_price', 'day_price', 'is_active')