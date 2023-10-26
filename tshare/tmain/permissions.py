from rest_framework import permissions


class IsUser(permissions.BasePermission):
    '''
    Класс доступа, который разрешает изменить пользовательские
    данные только самим пользователям
    '''
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsTransportOwner(permissions.BasePermission):
    '''
    Класс доступа, который разрешает изменить
    данные транспорта только его владельцам
    '''
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user