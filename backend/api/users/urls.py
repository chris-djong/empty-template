from django.conf.urls import url
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views


urlpatterns = [
    url(r'^api/token/refresh$', TokenRefreshView.as_view()),
    url(r'^api/register/resend-verification$',
        views.ResendVerificationEmailView.as_view()),
    url(r'^api/register$', views.UserRegistrationView.as_view()),
    url(r'^api/login$', views.UserLoginView.as_view()),
    url(r'^api/user-profile/send-forgot-password$',
        views.UserSendForgotPasswordView.as_view()),
    url(r'^api/user-profile/forgot-password/(?P<user_id>[0-9a-f-]+)/(?P<reset_token>[0-9a-z-]+)$',
        views.PasswordTokenView.as_view()),  # get request to verify the token
    url(r'^api/user-profile/change-password$',  # change the password
        views.UserPasswordChangeView.as_view()),
    url(r'^api/user-profile$', views.UserProfileView.as_view())
]
