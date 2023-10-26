from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, \
    DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tmain.permissions import IsTransportOwner
from tmain.serializers import *

###########################################################################
# Account

class CurrentUserBase:
    '''Базовый класс для AccountInfoAPIView и AccountUpdateAPIView'''
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class AccountInfoAPIView(CurrentUserBase, RetrieveAPIView):
    '''Представление просмотра данных пользователя (GET)'''

class AccountUpdateAPIView(CurrentUserBase, RetrieveUpdateAPIView):
    '''Представление обновления информации о пользователе (PUT, PATCH)'''

class AccountLogoutView(APIView):
    '''Представление выхода из аккаунта'''
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class AccountCreateAPIView(CreateAPIView):
    '''Регистрация пользователя'''
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

###########################################################################
# Transport

class TransportCreateAPIView(CreateAPIView):
    '''Создание нового транспорта'''
    serializer_class = TransportSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        # этот метод вызывается только при создании нового транспорта
        # тут автоматически назначается владелец ТС
        serializer.save(owner=self.request.user)

class TransportRUDAPIView(RetrieveUpdateDestroyAPIView):
    '''
    Класс, обрабатывающий запросы на обновление и удаление транспорта
    '''
    queryset = Transport.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return (AllowAny(),)

        return (IsAuthenticated(), IsTransportOwner())

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransportReadSerializer
        else:
            return TransportSerializer