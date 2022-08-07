from .models import NewsletterMail
from rest_framework import serializers

class NewsLetterMailSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsletterMail
        fields = '__all__'