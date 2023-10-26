from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from tmain.apps import user_registered
from tmain.models import *


###########################################################################
# Account serilizers
class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователя'''
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active',
                  'latitude', 'longitude', 'radius', 'send_messages',
                  'balance')
        extra_kwargs = {'is_active': {'read_only': True}}

class UserCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания пользователя'''
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.is_activated = False
        user.save()
        user_registered.send(UserCreateSerializer, instance=user)
        return user

class LogoutSerializer(serializers.Serializer):
    '''Сериализатор выхода'''
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('Bad token')

###########################################################################
# Transport serilizers

class TransportReadSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для чтения, где будут выводиться подробные данные об
    owner
    '''
    owner = UserSerializer(source=None)

    class Meta:
        model = Transport
        fields = ('id', 'transport_type', 'model', 'identifier', 'color',
                  'is_rented', 'is_active', 'description',
                  'latitude', 'longitude', 'hour_price', 'day_price',
                  'owner')

class TransportSerializer(serializers.ModelSerializer):
    '''
    Обычный сериализатор, который будет использовон для создания
    нового транспорта и обновления существующего
    '''
    class Meta:
        model = Transport
        fields = ('transport_type', 'model', 'identifier', 'color',
                  'is_active', 'description', 'latitude', 'longitude',
                  'hour_price', 'day_price')