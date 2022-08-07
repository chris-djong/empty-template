from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..stripe.models import Subscription, StripeSubscription
import os
import glob
from PIL import Image
from io import BytesIO
import datetime


# Serializer that creates a new user and the corresponding client and agent profiles
# All of the necessary directory to store user pictures and data are created
class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'sub_newsletter')
        extra_kwargs = {'password': {'write_only': True}}

    # Function to register a new user
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'],
                                        password=validated_data['password'], sub_newsletter=validated_data['sub_newsletter'])
        # Automatically assign the user to the free subscription
        free_subscription = Subscription.objects.get(name="Free")
        # Expiry date is set to
        expiry_date = datetime.datetime.today() + datetime.timedelta(30)
        StripeSubscription.objects.create(user=user, subscription=free_subscription, expiryDate=expiry_date, status="active")

        return user

# This serializer handles only validation of login state of the user
# It is called during login and checks whether passwords match and returns access and refresh tokens for user verification


class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=100, write_only=True)
    # user_picture = serializers.CharField(max_length=100, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # Convert username to email in case username is provided
        email = data.get("email", None)
        if '@' not in email:
            try:
                username = email.lower()
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'User with given email and password does not exist.')
            email = user.email
            user = None

        # Then authenticate the user using the provided password
        password = data.get("password", None)
        user = authenticate(email=email, password=password)

        # In case the authentication fails raise a validation error
        if user is None:
            raise serializers.ValidationError(
                'User with given email and password does not exist.')

        # Then check whether the user has verified his email already. If not raise an error as well.
        if not user.email_confirmed:
            raise serializers.ValidationError('User not verified.')

        # If the email has been confirmed and the authentication succeeded generate the tokens
        try:
            tokens = RefreshToken.for_user(user)
            refresh_token = str(tokens)
            access_token = str(tokens.access_token)
        except User.DoesNotExist:
            raise serializers.ValidationError('500 Internal server error.')

        return {'id': user.id, 'username': user.username, 'token': access_token, 'refresh': refresh_token}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
