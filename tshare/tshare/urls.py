"""
URL configuration for tshare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from tmain.rest_api_views import *

# router = DefaultRouter()
# router.register('account', AccountAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tmain.urls')),
    # rest api AccountController
    path('api/account/signup/', AccountCreateAPIView.as_view(), name='account-register'),
    path('api/account/signout/', AccountLogoutView.as_view(), name='account-signout'),
    path('api/account/me/', AccountInfoAPIView.as_view(), name='account-me'),
    path('api/account/update/', AccountUpdateAPIView.as_view(), name='account-update'),
    path('api/account/token/signin/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/account/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/account/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    # rest api TransportController
    path('api/transport/create/', TransportCreateAPIView.as_view(), name='transport-create'),
    path('api/transport/<int:pk>/', TransportRUDAPIView.as_view(), name='transport'),
    # rest api RentController
    path('api/rent/transporthistory/<int:pk>/', TransportRentHistoryAPIView.as_view(), name='transport-rent-history'),
    path('api/rent/transport/<int:pk>/', RentedOrOwnTransportAPIView.as_view(), name='rented-transport'),
    path('api/rent/end/<int:pk>/', EndRentAPIView.as_view(), name='end-rent'),
    path('api/rent/new/<int:pk>/', NewRentAPIView.as_view(), name='new-rent'),
    path('api/rent/transport/', RentAccessfulTransportAPIView.as_view(), name='accessful-transport'),
    path('api/rent/myhistory/', UserRentHistoryAPIView.as_view(), name='my-rent-history'),
    # rest api PaymentController
    path('api/payment/hesoyam/<int:pk>/', PaymentAPIView.as_view(), name='hesoyam'),
    # rest api AdminAccountController
    path('api/admin/account/<int:pk>/', AdminUserRUDAPIView.as_view(), name='admin-account-rud'),
    path('api/admin/account/', AdminAllUsersAPIView.as_view(), name='admin-account-listcreate'),

    # path('api/', include(router.urls)),
]
urlpatterns += [
    path('captcha/', include('captcha.urls')),
]