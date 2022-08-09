from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from ..users.models import User
from .models import NewsletterMail
from .serializers import NewsLetterMailSerializer
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken # for the immediate login 
import os 
import glob
from .functions import send_mail

# Endpoint that can be called to verifiy an email 
class VerifyEmailView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        user_id = data['userId']
        verificationToken = data['verificationToken']

        user = User.objects.get(id=user_id)
        # In case we have found the user verify the email                                                                                   
        if (user):
            # Check the token using the requested user
            # The token check is wrong when the user has either been logged in already or when the password has been changed
            token_check = default_token_generator.check_token(user, verificationToken)
            
            # If the token check is successful update the email verification status of the user and send a successful response
            if (token_check):
                user.email_confirmed = True
                user.save()
                
                # Whenever the token check was valid, we immediately log the user in as well 
                # ToDo: is this secure?? 
                tokens = RefreshToken.for_user(user)
                refresh_token = str(tokens)
                access_token = str(tokens.access_token)

                status_code = status.HTTP_200_OK
                response = {'id': user.id, 'username': user.username, 'token': access_token, 'refresh': refresh_token}
            # Otherwise send a 400 error 
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                response = {'message': 'Token invalid'}
        # And otherwise send a 404 response
        else:
            status_code = status.HTTP_404_NOT_FOUND
            response = {'message': 'Not found'}

        # And finally send the response that has been generated 
        return Response(response, status=status_code)
        
# Endpoint that is used to subscribe a user to the newsletter
class SubscribeNewsletterView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data

        serializer = NewsLetterMailSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            status_code = status.HTTP_200_OK
            response = {'message': 'successfully subscribed'}
            return Response(response, status=status_code)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = serializer.errors
            return Response(response, status=status_code)


