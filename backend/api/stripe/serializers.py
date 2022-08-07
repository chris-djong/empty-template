from rest_framework import serializers
from .models import Subscription, StripeSubscription

class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

class StripeSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StripeSubscription
        fields = '__all__'