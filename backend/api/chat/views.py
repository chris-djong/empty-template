from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q


from .models import Message
from .serializer import MessageSerializer

from ..users.models import User, Client


# Get all the messages that the logged in user has with the user that is passed as input
# Post request sends a message to the specific user that has been questioned
class MessagesByUserIdView(APIView):
    permission_classes = (IsAuthenticated, )
    # queryset = UploadedClientDocument.objects.all()
    # serializer_class =  UploadedClientDocumentSerializer

    def get(self, request, id):
        user = request.user
        contact = User.objects.get(id=identifier)

        # All the messages where we are on the receiving endpoint are set to read whenever they are retrieved
        received_messages = Message.objects.filter(sender=contact, recipient=user)
        received_messages.update(read=True)

        # Then retrieve all of the message for the endpoint itself 
        messages = Message.objects.filter( Q(sender=contact, recipient=user) | Q(sender=user, recipient=contact) )

        serialized_messages = MessageSerializer(messages, many=True)

        status_code = status.HTTP_200_OK
        return Response(serialized_messages.data, status=status_code)

    # Contact id is not used here. But as we use the same url we have to provide it anyway. 
    # Some minor security check to see whether the requestor know the protocol has been added
    def post(self, request, id):
        if (id != '12466d04-14ac-11ec-82a8-0242ac130003'):
            return Response({'msg': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # ToDo Add a condition that a user can not send a message to himself
        data = request.data
        sender = request.user
        identifier = data['recipientId']
        if (identifier.startswith('user-')):
            identifier = identifier.split('user-')[1]
            user = User.objects.get(id=identifier)
        else:
            client = Client.objects.get(id=identifier)
            user = client.user
            
        message = data['message']

        # And create the message    
        message = Message.objects.create(sender=sender, recipient=user, message=message)

        return Response({'msg': 'Message send successfully'}, status=status.HTTP_201_CREATED)

# Returns all current conversations of a given user
# Return all the  { name: 'Dan Mangers', lastMessage: 'Hey I will be there', unread: 1}
# Useful before the user can decide which messages he would like to view and to get an overview
class ConversationsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        # Obtain all the messages that the user is involved in
        messages = Message.objects.filter( Q(recipient=user) | Q(sender=user) )

        # And filter out the relevant data and the conversations
        # Messages are sorted by default
        conversations = []
        users = []
        for message in reversed(messages): 
            # First get the user that the message is corresponding too 
            if (message.sender == user):
                conversation_user = message.recipient
                send = True
            else:
                conversation_user = message.sender
                send = False
            
            # Then check whether we dont have the user already in the current conversations 
            # and add the corresponsing conversation
            if conversation_user not in users:
                # In case the message has been send by the user then  the conversation is assumed to be read automatically 
                if send:
                    read = True
                else:
                    # Else the status is dependant on the message itself
                    read = message.read
                    
                # We need to use the client id here so that the frontend is able to query more information about the user 
                try:
                    identifier = conversation_user.client.id
                except Client.DoesNotExist:
                    # Concat with user so that the frontend does not requet the client in that case 
                    # Examples are the noreply user that we have generated manually
                    identifier = 'user-' + str(conversation_user.id)
                conversations.append({'id': identifier, 'name': conversation_user.username, 'message': message.message, 'read': read, 'send': send, 'timestamp': message.timestamp})
                users.append(conversation_user)
        
        status_code = status.HTTP_200_OK
        return Response(conversations, status=status_code)


# API endpoint that simply returns whether there are unread conversations 
# This endpoint is queried at each refresh so 
class UnreadConversationsView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        # Check whether the user has received message which are unread 
        unread_messages = Message.objects.filter(recipient=user, read=False)

        if (unread_messages.count()):
            response = False
        else: 
            response = True
        status_code = status.HTTP_200_OK
        
        return Response(response, status_code)
