from django.db import models
import uuid
from ..users.models import User

# List of all the different subscriptions that we offer
# Make sure that they are up to date with the stripe subscriptions 
# This subsription is used to ensure what the user can do and what no 
# These models should be defined only once and after that they are not reuqired anymore by the backend
class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    description = models.CharField(max_length=254)
    priceMonthly = models.FloatField()
    priceMonthlyId = models.CharField(max_length=50, null=True)  # id that links the subscription to the corresponding stripe price for the monthly
    priceYearly = models.FloatField()
    priceYearlyId = models.CharField(max_length=50, null=True)  # id that links the subscription to the corresponding stripe price for the yearly


# The given stripe subscription is used to for payment processing etc 
# This is the subscription that determines whether the user has a valid subscription or not 
# This model should be used to identify whether the user is able to access certain variables
# It is linked to one of the subscriptions defined above 
class StripeSubscription(models.Model):
    uuiid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)  # the user itself use a one to one field because each user can only have one stripe subscription
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT)   # the subscription that is added to the customer 
    stripe_id = models.CharField(max_length=200, null=True)  # the id of the subscription in the stripe interface

    expiryDate = models.DateField()
    status = models.CharField(max_length=50, default="incomplete", choices=[('active', 'active'), ('incomplete', 'incomplete'), ('trialing', 'trialing'), ('incomplete_expired', 'incomplete_expired'), ('past_due', 'past_due'), ('canceled', 'canceled'), ('unpaid', 'unpaid')])
    invoice_status = models.CharField(max_length=50, null=True, choices=[('paid', 'paid'), ('open', 'open')])
    payment_intent_status = models.CharField(max_length=50, null=True, choices=[('succeeded', 'succeeded'), ('requires_payment_method', 'requires_payment_method'), ('requires_action', 'requires_action')])

    

