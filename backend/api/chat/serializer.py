from rest_framework import serializers
from .models import Message
from ..users.models import User

class MessageSerializer(serializers.ModelSerializer):
    
    sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    recipient = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Message
        fields = '__all__'
