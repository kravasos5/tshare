from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('rent/starting/', rent_starting, name='rent-strating'),

    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    path('accounts/register/activate/<str:sign>/', user_activate, name='register-activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register-done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register-user'),

    path('accounts/password/reset/confrim/<str:uidb64>/<str:token>/', PasswordResetConfrim.as_view(),
         name='password-reset-confrim'),
    path('accounts/password/reset/complete/', PasswordResetComplete.as_view(), name='password-reset-complete'),
    path('accounts/password/reset-done/', PasswordResetDone.as_view(), name='password-reset-done'),
    path('accounts/password/reset/', PasswordReset.as_view(), name='password-reset'),

    path('accounts/profile/delete/starting/', deleteUserStarting, name='profile-delete-starting'),
    path('accounts/profile/delete/<str:sign>/', DeleteUserView.as_view(), name='profile-delete'),

    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile-change'),

    path('accounts/profile/', profile, name='profile'),
]
