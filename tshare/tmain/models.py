from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    '''Модель пользователя'''
    balance = models.PositiveIntegerField(default=0, null=False,
                                          blank=False, verbose_name='Баланс')
    latitude = models.FloatField(verbose_name='Широта',
                                 help_text='Координаты пользователя по широте',
                                 validators=[
                                     MinValueValidator(-180),
                                     MaxValueValidator(180)
                                 ],
                                 null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота',
                                  help_text='Координаты пользователя по долготе',
                                  validators=[
                                      MinValueValidator(-90),
                                      MaxValueValidator(90)
                                  ],
                                  null=True, blank=True)
    radius = models.PositiveSmallIntegerField(verbose_name='Радиус поиска ТС',
                                              default=30)
    is_activated = models.BooleanField(default=True,
                   verbose_name='Активирован ли пользователь')
    send_messages = models.BooleanField(default=False,
                   verbose_name='Отправлять ли оповещения?')

def validate_identifier(val):
    '''Валидатор идентификатора ТС'''
    if len(val) != 10:
        raise ValidationError('Идентификатор ТС должен быть длинной 10 символов',
                              code='invalid')

def validate_gt_zero(val):
    '''Валидатор, проверяющий положительное ли значение'''
    if val < 0:
        raise ValidationError('Введённое значение должно быть больше нуля',
                              code='invalid')

class Transport(models.Model):
    '''Модель ТС'''
    transport_types = [
        ('c', 'Машина'),
        ('m', 'Мотоцикл'),
        ('s', 'Самокат')
    ]
    is_rented = models.BooleanField(default=False, verbose_name='Арендовано ли ТС?')
    is_active = models.BooleanField(default=True, verbose_name='Доступно ли ТС для аренды?')
    transport_type = models.CharField(max_length=1, choices=transport_types)
    model = models.CharField(max_length=100, verbose_name='Модель ТС')
    color = models.CharField(max_length=80, verbose_name='Цвет ТС')
    identifier = models.CharField(validators=(validate_identifier,),
                                  verbose_name='Идентификатор ТС')
    description = models.CharField(verbose_name='Описание ТС',
                                   max_length=500,
                                   help_text='Максимальная длина описания \
                                              - 500 символов')
    latitude = models.IntegerField(verbose_name='Широта',
                                 help_text='Координаты ТС по широте',
                                 validators=[
                                     MinValueValidator(-180),
                                     MaxValueValidator(180)
                                 ])
    longitude = models.IntegerField(verbose_name='Долгота',
                                  help_text='Координаты ТС по долготе',
                                  validators=[
                                      MinValueValidator(-90),
                                      MaxValueValidator(90)
                                  ])
    hour_price = models.FloatField(verbose_name='Цена аренды за час',
                                   validators=(validate_gt_zero,))
    day_price = models.FloatField(verbose_name='Цена аренды за 1 сутки',
                                  validators=(validate_gt_zero,))
    owner = models.ForeignKey(User, verbose_name='Владелец ТС', on_delete=models.CASCADE)

    def get_transport_type_display(self):
        return dict(self.transport_types)[self.transport_type]

    def __str__(self):
        return f'{self.get_transport_type_display()} - {self.model}'

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

class RentManager(models.Manager):
    '''Менеджер аренды'''
    def get_queryset(self):
        return super().get_queryset() \
            .select_related('user', 'transport')

class Rent(models.Model):
    '''Модель аренды'''
    objects = RentManager()

    user = models.ForeignKey(User, verbose_name='Арендатор', on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, verbose_name='ТС', on_delete=models.CASCADE)
    time_start = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата начала аренды')
    time_end = models.DateTimeField(null=True, blank=True,
                                    verbose_name='Дата конца аренды')
    is_active = models.BooleanField(default=True,
                                    verbose_name='Активна ли аренда?')
    price = models.FloatField(verbose_name='Цена аренды',
                              validators=(validate_gt_zero,),
                              null=True, blank=True)

    def __str__(self):
        return f'Аренда: {self.user} - {self.transport}'

    def get_duration(self):
        print(self.time_end)
        if self.time_end != None:
            duration = self.time_end - self.time_start
        else:
            duration = timezone.now() - self.time_start
        return duration

    def get_rental_duration(self):
        duration = self.get_duration()
        days = duration.days
        hours = (duration.seconds // 3600) - days * 24
        minutes = (duration.seconds // 60) - hours * 60
        return f'Дни: {days}; часы: {hours}; минуты: {minutes}'

    def get_rental_price(self):
        duration = self.get_duration()
        price = (duration.seconds / 3600) * self.transport.hour_price
        return f'{round(price, 2)}'

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'