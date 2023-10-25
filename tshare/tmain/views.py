from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.db.models import ExpressionWrapper, F, fields
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from django.contrib import messages

from .apps import user_delete_signal
from .forms import ChangeUserInfoForm, RegisterUserForm, DeleteUserForm, UserTransportForm
from .mixins import CsrfMixin
from .models import User, Transport, Rent
from .utilities import signer


def main(request):
    '''Главная'''
    return render(request, 'tmain/main.html', context={})

class RentStartingView(CsrfMixin, TemplateView):
    '''Представление начала аренды'''
    template_name = 'tmain/rent_starting.html'

    def get(self, request):
        context = self.get_context_data()
        tt = [x[-1] for x in Transport.transport_types]
        context['transport_types'] = tt
        return render(request, 'tmain/rent_starting.html', context=context)

class RentView(LoginRequiredMixin, SuccessMessageMixin, CsrfMixin, TemplateView):
    '''Начало аредны'''
    template_name = 'tmain/rent.html'

    def get(self, request, type):
        context = self.get_context_data()
        transport = Transport.objects.filter(is_rented=False, is_active=True,
                                             transport_type=type) \
                                .exclude(owner=request.user)
        context['ts_is_empty'] = not transport.exists()
        context['transport'] = transport
        return render(request, 'tmain/rent.html', context=context)

    def post(self, request, *args, **kwargs):
        try:
            # извлекаю id ТС
            ts_id = request.POST.get('ts_id')
            # нахожу ТС и меняю поле is_rented на True
            # это значит, что транспорт теперь отмечен,
            # как арендованный
            ts = Transport.objects.get(id=ts_id)
            ts.is_rented = True
            ts.save()
            # создаю новую аренду
            Rent.objects.create(user=request.user,
                                transport=ts,
                                is_active=True)
            return JsonResponse(data={}, status=200)
        except Exception as ex:
            print(ex)
            return JsonResponse(data={'ex': f'Ошибка: {ex}'}, status=500)

class UserTransportView(CsrfMixin, LoginRequiredMixin, TemplateView):
    '''Представление просмотра'''
    template_name = 'tmain/user_transport.html'

    def get(self, request):
        context = super().get_context_data()
        user_ts = Transport.objects.filter(owner=request.user)
        usert_ts_is_empty = not user_ts.exists()
        context['transport'] = user_ts
        context['usert_ts_is_empty'] = usert_ts_is_empty
        return render(request, 'tmain/user_transport.html', context=context)

    def post(self, request, *args, **kwargs):
        try:
            # получаю id транспорта и нахожу его
            ts_id = request.POST.get('ts_id')
            # получаю и удаляю транспортное средство
            ts = Transport.objects.get(id=ts_id)
            if ts:
                ts.delete()
            return JsonResponse(data={}, status=200)
        except Exception as ex:
            print(ex)
            return JsonResponse(data={'ex': f'Ошибка: {ex}'}, status=500)

class UserTransportCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    '''Представление создания нового ТС'''
    model = Transport
    template_name = 'tmain/create_user_transport.html'
    form_class = UserTransportForm
    success_url = reverse_lazy('profile-transport')
    success_message = 'Новое ТС успешно создано'

    def post(self, request, *args, **kwargs):
        form = UserTransportForm(request.POST)
        if form.is_valid():
            # Автоматически присвоит владельца ТС
            transport = form.save(commit=False)
            transport.owner = request.user
            transport.save()
            return redirect('profile-transport')
        else:
            form = UserTransportForm()
            return render(request, 'create_user_transport.html', context={'form': form})

class UserTransportUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    '''Представление обновления ТС'''
    model = Transport
    template_name = 'tmain/update_user_transport.html'
    form_class = UserTransportForm
    success_url = reverse_lazy('profile-transport')
    success_message = 'ТС успешно изменено'

# Разграничение доступа
class LoginView(LoginView):
    '''Вход в аккаунт'''
    template_name = 'tmain/login.html'

class LogoutView(LoginRequiredMixin, LogoutView):
    '''Выход из профиля'''
    template_name = 'tmain/logout.html'

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    '''Изменение пользовательской информации'''
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

class Profile(LoginRequiredMixin, CsrfMixin, TemplateView):
    '''Страница пользователя'''
    template_name = 'tmain/profile.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        rents = Rent.objects.filter(user=request.user, is_active=True)
        context['rents_is_empty'] = not rents.exists()
        context['rents'] = rents
        return render(request, 'tmain/profile.html', context=context)

    def post(self, request, *args, **kwargs):
        try:
            # извлекаю id аренды
            rent_id = request.POST.get('rent_id')
            # нахожу её
            rent = Rent.objects.get(id=rent_id)
            # делаю неактивной, обновляю цену аренды и дату окончания аренды
            rent.is_active = False
            rent.price = rent.get_rental_price()
            rent.time_end = timezone.now()
            # ообновляю ТС, is_rented=False, чтобы его можно было арендовать снова
            rent.transport.is_rented = False
            rent.transport.save()
            # нахожу пользователя и обновляю ему баланс
            user = rent.user
            user.balance = user.balance - float(rent.get_rental_price())
            user.save()
            # обновляю аренду
            rent.save()
            return JsonResponse(data={'new_balance': user.balance}, status=200)
        except Exception as ex:
            return JsonResponse(data={'ex': f'Ошибка: {ex}'}, status=500)

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