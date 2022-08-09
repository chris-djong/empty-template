from ast import Pass
from api.stripe.models import Subscription
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .models import User
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from ..emails.functions import send_mail

from PIL import Image, ExifTags
from io import BytesIO
import base64
import os
import glob


"""
    Post request toregister a new user
    The request generate a verification link and sends it to the user
"""


class UserRegistrationView(CreateAPIView):

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate an email verification token
            verification_token = default_token_generator.make_token(user)
            verificationLink = '<addWebsiteHere>/login/{}/{}'.format(
                verification_token, user.id)

            # Send registration email
            context = {'verificationLink': verificationLink,
                       'username': user.username}
            send_mail('[addEmailHere]', [user.email], 'Welcome to [add Name of Website here]',
                      'register', context=context)

            status_code = status.HTTP_201_CREATED
            response = {
                'success': 'True',
                'status code': status_code,
                'message': 'User registered  successfully',
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': serializer.errors}
        return Response(response, status=status_code)


class UserLoginView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # In case the credentials are valid return everything
            response = serializer.validated_data
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': serializer.errors}
        return Response(response, status=status_code)


""" This endpoint is used by the user in the settings to change his password
 It requires both the old and the new password """


class UserPasswordChangeView(APIView):
    permission_classes = (IsAuthenticated, )

    def put(self, request):
        data = request.data
        current_password = request.data['currentPassword']

        new_password = data['newPassword']
        confirm_new_password = data['confirmNewPassword']
        user = request.user
        # Add password validation
        if new_password == confirm_new_password:
            if check_password(current_password, user.password):
                user.set_password(new_password)
                user.save()
                response = {'message': 'Password change successfully.'}
                status_code = status.HTTP_200_OK
            else:
                response = {'message': 'Current password is not valid.'}
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': 'New password does not match.'}
        return Response(response, status=status_code)


""" This endpoint resend  the email verification the authenticated user
    It only works in case the user is not verified already and in case
    the user provided correct authentication details """


class ResendVerificationEmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        data = request.data
        email = data['email']
        password = data['password']

        # Retrieve the email that belongs to the user
        if '@' not in email:
            try:
                username = email.lower()
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                status_code = status.HTTP_400_BAD_REQUEST
                response = {'message': 'Wrong credentials.'}
                return Response(response, status=status_code)

            # In case we have found the user retrieve his email
            email = user.email
            user = None

        # Then authenticate the user using the provided password
        user = authenticate(email=email, password=password)
        # In case the authentication fails raise a validation error
        if user is None:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': 'Wrong credentials.'}
            return Response(response, status=status_code)

        # Otherwise generate the verification token and send the mail
        verification_token = default_token_generator.make_token(user)
        verificationLink = '<addWebsiteHere>/login/{}/{}'.format(
            verification_token, user.id)

        # Send registration email
        context = {'verificationLink': verificationLink,
                   'username': user.username}
        send_mail('addEmailHere', [user.email], 'Welcome to [addNameOfWebsiteHere]',
                  'register', context=context)

        status_code = status.HTTP_200_OK
        response = {}
        return Response(response, status=status_code)


""" View that sends the corresponding user a token to regenerate his password in case he has forgotten it """


class UserSendForgotPasswordView(APIView):
    permission_classes = (AllowAny, )

    def put(self, request):
        # Retrieve the inputs which is only the email
        email = request.data['email']
        user = User.objects.filter(email=email)
        # In case we have not user simply pass the request back and do no further processing
        if (user.count() != 1):
            status_code = status.HTTP_200_OK
            response = {}
            return Response(response, status=status_code)
        else:
            user = user[0]

        # Else generate the custom token for the password reset
        resetToken = PasswordResetTokenGenerator().make_token(user)
        resetLink = '<addWebsiteHere>/password-reset/{}/{}'.format(
            user.id, resetToken)

        # Send password reset email
        context = {'resetLink': resetLink,
                   'username': user.username}
        send_mail('<addEmailHere>', [user.email], 'Password reset',
                  'password_reset', context=context)

        # Resending password
        status_code = status.HTTP_200_OK
        response = {}
        return Response(response, status=status_code)


""" View to check whether a password reset token is valid or that makes it possible to change the password """


class PasswordTokenView(APIView):
    permission_classes = (AllowAny, )

    # Endpoint to check whether a token is valid returns either true or false
    def get(self, request, user_id, reset_token):
        # First retrieve the user object itself
        user = User.objects.filter(id=user_id)
        if (user.count() != 1):
            status_code = status.HTTP_400_BAD_REQUEST
            response = {}
            return Response(response, status_code)
        else:
            user = user[0]

        tokenValid = PasswordResetTokenGenerator().check_token(user, reset_token)

        status_code = status.HTTP_200_OK
        response = tokenValid
        return Response(response, status=status_code)

    # Endpoint to reset the password itself
    # Needs the password and the confirmed password in the body
    def post(self, request, user_id, reset_token):
        # Random check which has no use at all but has been setup so that we can use the same url
        if (not (user_id == 'd8fde17f-614d-4619-afa1-88ffd405473f' and reset_token == 'a4a1298f-88fa-4732-b6cf-114da5bcb82b')):
            status_code = status.HTTP_400_BAD_REQUEST
            response = {}
            return Response(response, status_code)

        # Retrieve the data
        data = request.data
        # The form itself contain email and passwod information
        form = data['formData']
        password = form['password']
        passwordConfirmation = form['passwordConfirmation']
        email = form['email']

        # User id and token are provided in the data object itself
        userId = data['userId']
        resetToken = data['token']

        # Get the corresponding user and check his password and token
        # This ensure that the corresponding token is only able to change the corresponding password
        user = User.objects.get(id=userId)

        # Check whether the user provided the correct email (only a small further check but has not significant meaning in the end)
        if (user.email != email):
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': 'Invalid email'}
            return Response(response, status_code)

        tokenValid = PasswordResetTokenGenerator().check_token(user, resetToken)
        if (not tokenValid):
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': 'Invalid token'}
            return Response(response, status_code)

        # And finally check whether the passwords are the same
        if (password != passwordConfirmation):
            status_code = status.HTTP_400_BAD_REQUEST
            response = {'message': 'Passwords do not match'}
            return Response(response, status_code)

        # In case all checks are good we change the password itself
        user.set_password(password)
        user.save()

        status_code = status.HTTP_200_OK
        response = {}
        return Response(response, status=status_code)

# View that is used to obtain user profile information from onself
# The view is only used for authenticated users and as such the post request is used to change its settings


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        response = {}

        # Set the required data by the get request
        response['username'] = user.username
        response['email'] = user.email
        response['sub_newsletter'] = user.sub_newsletter

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)

    def put(self, request):
        user = request.user
        data = request.data

        # Update the fields
        user.username = data['username']

        # Todo username validation
        if data['email'] != user.email:
            user.email = data['email']
            # ToDo send verification email
        user.phone_number = data['phone_number']

        # Whenever we allow the user to upload links use this if
        # elif ('link' in data['gallery'][0].keys()):

        user.sub_newsletter = data['sub_newsletter']
        user.save()

        status_code = status.HTTP_200_OK
        response = {}
        return Response(response, status=status_code)


