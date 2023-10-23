from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from django.contrib import messages

from .apps import user_delete_signal
from .forms import ChangeUserInfoForm, RegisterUserForm, DeleteUserForm
from .models import User
from .utilities import signer


def main(request):
    '''Главная'''
    return render(request, 'tmain/main.html', context={})

def rent_starting(request):
    '''Начало аредны'''
    return render(request, 'tmain/rent_starting.html', context={})

# Разграничение доступа
class LoginView(LoginView):
    '''Вход в аккаунт'''
    template_name = 'tmain/login.html'

class LogoutView(LoginRequiredMixin, LogoutView):
    '''Выход из профиля'''
    template_name = 'tmain/logout.html'

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'tmain/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('profile')
    success_message = 'Данные успешно изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.user_id)

@login_required
def profile(request):
    '''Страница пользователя'''
    return render(request, 'tmain/profile.html')

class RegisterUserView(CreateView):
    '''Регистрация пользователя'''
    model = User
    template_name = 'tmain/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('register-done')

class RegisterDoneView(TemplateView):
    '''Завершение регистрации'''
    template_name = 'tmain/register_done.html'

def user_activate(request, sign):
    '''Активация пользователя'''
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'tmain/bad_signature.html')
    user = get_object_or_404(User, username=username)
    if user.is_activated:
        template = 'tmain/user_is_activated.html'
    else:
        template = 'tmain/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

# Удаление пользователя
@login_required
def deleteUserStarting(request):
    protocol = request.scheme
    domain = request.get_host()
    user_delete_signal.send('deleteUserStarting', instance=request.user, protocol=protocol, domain=domain)
    return render(request, 'tmain/delete_user_starting.html')

class DeleteUserView(LoginRequiredMixin, DeleteView):
    '''Удаление аккаунта пользователя'''
    model = User
    template_name = 'tmain/delete_user.html'
    success_url = reverse_lazy('main')
    form_class = DeleteUserForm

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.get(id=self.user_id)
            if username == user.username and user.check_password(password):
                logout(request)
                messages.add_message(request, messages.SUCCESS,
                                     'Пользователь удалён')
                return super().post(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.ERROR, "Поля заполнены неверно")
                return render(request, 'tmain/delete_user.html', {'form': form})
        else:
            messages.add_message(request, messages.ERROR, "Неправильная форма")
            return render(request, 'tmain/delete_user.html', {'form': form})

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.user_id)

# Сброс пароля
class PasswordReset(PasswordResetView):
    '''Представление сброса пароля'''
    template_name = 'tmain/password_reset.html'
    html_email_template_name = 'email/reset_letter_body.html'
    email_template_name = 'email/reset_letter_body.txt'
    subject_template_name = 'email/reset_letter_subject.txt'
    success_url = reverse_lazy('password-reset-done')

class PasswordResetDone(PasswordResetDoneView):
    '''Оповещение о отправленном письме'''
    template_name = 'tmain/password_reset_done.html'

class PasswordResetConfrim(PasswordResetConfirmView):
    '''Представление подтверждения сброса пароля (ввод нового пароля)'''
    template_name = 'tmain/password_reset_confirm.html'
    success_url = reverse_lazy('password-reset-complete')

class PasswordResetComplete(PasswordResetCompleteView):
    '''Пароль успешно сброшен'''
    template_name = 'tmain/password_reset_complete.html'