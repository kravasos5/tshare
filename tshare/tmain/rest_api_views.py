from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, \
    DestroyAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tmain.permissions import *
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

###########################################################################
# Rent

class RentAccessfulTransportAPIView(ListAPIView):
    '''Представление вывода доступного для аренды транспорта'''
    serializer_class = TransportReadSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.request.user == AnonymousUser:
            return Transport.objects.filter(is_rented=False, is_active=True) \
                .exclude(owner=self.request.user)
        else:
            return Transport.objects.filter(is_rented=False, is_active=True)

class RentedOrOwnTransportAPIView(RetrieveAPIView):
    '''Получение информации о транспорте арендатором или владельцем'''
    serializer_class = TransportReadSerializer
    permission_classes = (IsTransportRenterOrOwner,)
    queryset = Transport.objects.all()

class UserRentHistoryAPIView(ListAPIView):
    '''Представление истории аренд пользователя'''
    serializer_class = RentReadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Rent.objects.filter(user=self.request.user) \
            .order_by('-time_start')

class TransportRentHistoryAPIView(ListAPIView):
    '''Представление истории аренд транспорта'''
    serializer_class = RentReadSerializer
    permission_classes = (IsAuthenticated, IsRentedTransportOwner)

    def get_queryset(self):
        return Rent.objects.filter(transport=self.kwargs.get('pk')) \
                .order_by('-time_start')

class NewRentAPIView(APIView):
    '''Представление новой аренды'''
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            ts = Transport.objects.get(id=pk)
        except Exception as ex:
            return Response({'message': 'ТС не найдено'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user == ts.owner:
            return Response({'message': 'Нельзя арендовать собственное ТС'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif user.balance < ts.hour_price:
            return Response({'message': 'Не хватает денег на аренду ТС'}, status=status.HTTP_402_PAYMENT_REQUIRED)


        rent = Rent.objects.create(user=user, transport=ts)
        serialized_rent = RentReadSerializer(rent)
        return Response({'message': 'Новая аренда успешно создана', 'rent': serialized_rent.data})


class EndRentAPIView(APIView):
    '''Представление заверешения аренды'''
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            rent = Rent.objects.get(pk=pk)
        except Rent.DoesNotExist:
            return Response({'message': 'Аренда не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != rent.user:
            return Response({'message': 'У вас нет прав на завершение этой аренды'},
                            status=status.HTTP_403_FORBIDDEN)

        if rent.is_active == False:
            return Response({'message': 'Эта аренда уже завершена'},
                            status=status.HTTP_403_FORBIDDEN)

        # делаю неактивной, обновляю цену аренды и дату окончания аренды
        rent.is_active = False
        print(rent.get_rental_price())

        rent.price = rent.get_rental_price()
        rent.time_end = timezone.now()
        # ообновляю ТС, is_rented=False, чтобы его можно было арендовать снова
        rent.transport.is_rented = False
        rent.transport.save()
        # нахожу пользователя и обновляю ему баланс
        user = rent.user
        user.balance = user.balance - float(rent.price)
        user.save()
        # обновляю аренду
        rent.save()

        return Response({'message': 'Аренда завершена успешно'}, status=status.HTTP_200_OK)

###########################################################################
# Payment
class PaymentAPIView(APIView):
    '''Представление добавления денег на счёт пользователя'''
    permission_classes = (IsAuthenticated, IsUserOrAdmin)

    def post(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except Exception as ex:
            return Response({'message': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        user.balance = user.balance + 250000
        user.save()
        serializer = UserSerializer(user)
        return Response({'message': 'Средства успешно добавлены', 'user': serializer.data}, status=status.HTTP_200_OK)

###########################################################################
# AdminAccountController
class AdminAllUsersAPIView(ListCreateAPIView):
    '''Получение всех аккаунтов'''
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        if self.request.method == 'GET':
            queryset = User.objects.all().order_by('id')[self.start:self.start+self.count]
            return queryset
        else:
            return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminUserSerializer
        else:
            return AdminUserCreateSerializer

    def get(self, request, *args, **kwargs):
        try:
            print(request.data.get('start'))
            print(request.data.get('count'))
            self.start = int(request.data.get('start'))
            self.count = int(request.data.get('count'))
        except Exception as ex:
            return Response({'message': 'Не указан start или count или они указаны в неверном формате'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

class AdminUserRUDAPIView(RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) пользователя админом
    '''
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()