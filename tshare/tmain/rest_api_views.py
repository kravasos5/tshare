from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView, \
    RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView
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

        self.rent_end(rent)

        return Response({'message': 'Аренда завершена успешно'}, status=status.HTTP_200_OK)

    def rent_end(self, rent):
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

class AdminPermissionBase:
    permission_classes = (IsAdminUser,)

class AdminListStartCountBase:
    '''
    Базовый класс для админ-классов, где нужно выводить список от start
    и где есть count
    '''
    def get_queryset(self):
        '''
        Если метод GET, то выбираю от start до count + start,
        иначе выбираю все записи
        '''
        if self.request.method == 'GET':
            queryset = self.model.objects.all().order_by('id')[self.start:self.start+self.count]
            return queryset
        else:
            return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            self.start = int(request.data.get('start'))
            self.count = int(request.data.get('count'))
        except Exception as ex:
            return Response({'message': 'Не указан start или count или они указаны в неверном формате'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

class AdminAllUsersAPIView(AdminListStartCountBase, AdminPermissionBase, ListCreateAPIView):
    '''Получение всех аккаунтов'''
    model = User

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminUserSerializer
        else:
            return AdminUserCreateSerializer

class AdminUserRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) пользователя админом
    '''
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

###########################################################################
# AdminTransportController

class AdminAllTransportAPIView(AdminListStartCountBase, AdminPermissionBase, ListCreateAPIView):
    '''Получение всех аккаунтов'''
    model = Transport

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransportReadSerializer
        else:
            return AdminTransportSerializer

class AdminTransportRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) транспорта админом
    '''
    serializer_class = AdminTransportSerializer
    queryset = Transport.objects.all()

###########################################################################
# AdminRentController

class AdminRentRUDAPIView(AdminPermissionBase, RetrieveUpdateDestroyAPIView):
    '''
    Представление получения (GET), обновления (PUT, PATCH) и
    удаления (DELETE) аренды админом
    '''
    queryset = Rent.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminRentReadSerializer
        else:
            return AdminRentSerializer

class AdminUserRentHistoryAPIView(AdminPermissionBase, UserRentHistoryAPIView):
    '''Получение истории аренд пользователя'''
    serializer_class = AdminRentReadSerializerShort
    def get_queryset(self):
        return Rent.objects.filter(user__id=self.kwargs.get('pk')) \
            .order_by('-time_start')

class AdminTransportRentHistoryAPIView(AdminPermissionBase, TransportRentHistoryAPIView):
    '''Получение истории аренд транспорта'''
    serializer_class = AdminRentReadSerializerShort

class AdminNewRentAPIView(AdminPermissionBase, APIView):
    '''Представление создания новой аренды'''

    def post(self, request):
        try:
            user_id = request.data.get('user')
            transport_id = request.data.get('transport')
        except Exception as ex:
            return Response({'message': 'Не указан один из атрибутов: user или transport'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        ts = Transport.objects.get(id=transport_id)
        if user == ts.owner:
            return Response({'message': 'Нельзя арендовать собственное ТС'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif user.balance < ts.hour_price:
            return Response({'message': 'Не хватает денег на аренду ТС'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        rent = Rent.objects.create(user=user, transport=ts)
        serialized_rent = AdminRentReadSerializerShort(rent)
        return Response({'message': 'Новая аренда успешно создана', 'rent': serialized_rent.data})

class AdminEndRentAPIView(AdminPermissionBase, EndRentAPIView):
    '''Представление завершения аренды'''

    def post(self, request, pk):
        try:
            rent = Rent.objects.get(pk=pk)
        except Rent.DoesNotExist:
            return Response({'message': 'Аренда не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if rent.is_active == False:
            return Response({'message': 'Эта аренда уже завершена'},
                            status=status.HTTP_403_FORBIDDEN)

        self.rent_end(rent)

        return Response({'message': 'Аренда завершена успешно'}, status=status.HTTP_200_OK)
