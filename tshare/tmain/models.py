from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

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