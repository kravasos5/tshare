import datetime

from django.contrib import admin
from .models import *

# Рассылка писем с требованием пройти активацию
from .utilities import send_activation_notification


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с требованиями отправлены')
send_activation_notifications.short_description = 'Отправка писем' \
'с требованиями активации'


class NonactivatedFilter(admin.SimpleListFilter):
    '''Фильтр пользователей, прошедших активацию'''
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return [
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif self.value() == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)
        elif self.value() == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)


class UserAdmin(admin.ModelAdmin):
    '''Редактор ползователя'''
    list_display = ('__str__', 'is_activated', 'date_joined', 'balance',
                    'latitude', 'longitude', 'radius')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = [NonactivatedFilter]
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('latitude', 'longitude', 'radius'),
              'balance',
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    exclude = ('slug',)
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)

class TransportAdmin(admin.ModelAdmin):
    '''Редактор транспорта'''
    list_display = ('__str__', 'is_rented', 'is_active', 'transport_type', 'model',
                    'color', 'identifier', 'description', 'latitude',
                    'longitude', 'hour_price', 'day_price', 'owner')
    search_fields = ('transport_type', 'identifier', 'owner', 'is_rented',
                     'is_active')
    fields = (
        'is_rented', 'is_active',
        ('transport_type', 'identifier'),
        ('model', 'color', 'description'),
        ('latitude', 'longitude'),
        ('hour_price', 'day_price'),
        'owner'
    )
    readonly_fields = ('is_rented',)

class RentAdmin(admin.ModelAdmin):
    '''Редактор аренды'''
    list_display = ('user', 'transport', 'time_start', 'time_end',
                    'is_active', 'price')
    search_fields = ('user', 'transport', 'is_active',
                     'time_start', 'time_end')
    fields = (
        'user', 'transport', 'is_active',
        'time_end',
        'price'
    )
    readonly_fields = ('time_start',)

admin.site.register(User, UserAdmin)
admin.site.register(Transport, TransportAdmin)
admin.site.register(Rent, RentAdmin)
