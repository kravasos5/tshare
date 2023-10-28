from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .yasg import urlpatterns as ysag_urlpatterns

from tmain.rest_api_views import *


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
    # rest api AdminTransportController
    path('api/admin/transport/<int:pk>/', AdminTransportRUDAPIView.as_view(), name='admin-transport-rud'),
    path('api/admin/transport/', AdminAllTransportAPIView.as_view(), name='admin-transport-listcreate'),
    # rest api AdminRentController
    path('api/admin/rent/end/<int:pk>/', AdminEndRentAPIView.as_view(), name='admin-end-rent'),
    path('api/admin/rent/<int:pk>/', AdminRentRUDAPIView.as_view(), name='admin-transport-rud'),
    path('api/admin/rent/', AdminNewRentAPIView.as_view(), name='admin-new-rent'),
    path('api/admin/userhistory/<int:pk>/', AdminUserRentHistoryAPIView.as_view(), name='admin-user-history'),
    path('api/admin/transporthistory/<int:pk>/', AdminTransportRentHistoryAPIView.as_view(), name='admin-transport-rent-history'),
]

urlpatterns += [
    path('captcha/', include('captcha.urls')),
]

urlpatterns += ysag_urlpatterns