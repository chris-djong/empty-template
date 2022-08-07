import stripe
from .models import Subscription, StripeSubscription
import datetime
from ..users.models import User
from ..properties.functions import disable_excessive_properties
import os

stripe.api_key = os.environ['STRIPE_KEY']


# This function creates a stripe customer based on the input data
# Input: data = {email: , }
# Output: As output we return the stripe customer itself
def create_customer(data):
    try:
        # Create a new customer object
        customer = stripe.Customer.create(email=data['email'])

        return customer
    # In case of an error print the error and return 0
    except Exception as e:
        print(e)
        return 0


# This function takes the data obtained by the webhook and updates the stripe subscription
# The data object needs to have at least the following fields for this to work: subscription and customer
def update_subscription_from_webhook(data):
    # Relieve relevant data from the input data
    if 'customer' in data.keys():
        customer_id = data['customer']
    else:
        print("Could not retrieve customer id from webhook object")
        print(data)
        return

    # Either we provide the id of the subscription in the subscription field
    if 'subscription' in data.keys():
        subscription_id = data['subscription']
    # Or else it is possible that the id is retrieved from the object itself
    elif data['object'] == 'subscription':
        subscription_id = data['id']
    # Else return with an error
    else:
        print("Could not retrieve subscription id from webhook object")
        print(data)
        return

    # Get the actual and valid user data from stripe side
    stripe_cloud_subscription = stripe.Subscription.retrieve(
        subscription_id)
    price_id = stripe_cloud_subscription['plan']['id']
    # Retrieve the subscription status active / incomplete
    subscription_status = stripe_cloud_subscription['status']

    # Retrieve the subscription end period and add two days for now so that the customer has time to adapt to errors in code
    period_end = stripe_cloud_subscription['current_period_end'] + 2*24*60*60
    date_end = datetime.date.fromtimestamp(period_end)
    interval = stripe_cloud_subscription['items']['data'][0]['plan']['interval']
    # We can now get the data from our interface
    # First the user
    user = User.objects.get(stripe_customer_id=customer_id)
    # Then based on the subscription interval we get the subscription itself
    if (interval == "month"):
        subscription = Subscription.objects.get(
            priceMonthlyId=price_id)
    elif (interval == "year"):
        subscription = Subscription.objects.get(priceYearlyId=price_id)

    # And finally we update the data in the stripe subscription from our side
    stripe_subscriptions = StripeSubscription.objects.filter(user=user)
    # In case the user had a subscription already update it with the new values
    if (stripe_subscriptions.count() == 1):
        stripe_subscription = stripe_subscriptions[0]
        stripe_subscription.subscription = subscription
        stripe_subscription.status = subscription_status
        stripe_subscription.expiryDate = date_end
    # And otherwise create a subscription that contains the new data
    elif (stripe_subscriptions.count() == 0):
        stripe_subscription = StripeSubscription.objects.create(
            user=user, subscription=subscription, stripe_id=subscription_id, status=subscription_status, expiryDate=date_end)
    # This case should never happen so just print an error so that we can follow it
    else:
        print("Multiple subscriptions for given user have been found. Dont know what to do here. User:", user)

    # And save the final stripe subscription object on our end so that the user gets access
    stripe_subscription.save()

    disable_excessive_properties(user)

    return
