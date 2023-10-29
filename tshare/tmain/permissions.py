from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from tmain.models import Rent, Transport


class IsUserOrAdmin(permissions.BasePermission):
    '''
    Класс доступа, который проверяет является ли пользователь
    из запроса пользователем, id которого передан, как параметр pk
    в маршруте или является ли пользователь админом
    '''
    def has_permission(self, request, view):
        return request.user.is_superuser or view.kwargs.get('pk') == request.user.id

class IsTransportOwner(permissions.BasePermission):
    '''
    Класс доступа, который разрешает изменить
    данные транспорта только его владельцам
    '''
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsTransportRenterOrOwner(permissions.BasePermission):
    '''
    Класс доступа, который разрешает получить
    данные транспорта только его арендаторам
    '''
    def has_object_permission(self, request, view, obj):
        r = Rent.objects.filter(is_active=True, transport=obj.id)
        if len(r) == 0:
            return obj.owner == request.user
        return request.user.id in list(r.values('user'))[0].values() or obj.owner == request.user

class IsRentedTransportOwner(permissions.BasePermission):
    '''
    Класс доступа, который разрешает изменить
    данные транспорта только его владельцам
    '''
    def has_permission(self, request, view):
        owner = Transport.objects.get(id=view.kwargs.get('pk')).owner
        return request.method in SAFE_METHODS and request.user == owner

