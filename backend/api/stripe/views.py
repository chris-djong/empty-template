from email.policy import default
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Subscription, StripeSubscription
from .functions import update_subscription_from_webhook
from .serializers import SubscriptionSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from ..users.models import User
import datetime
from .models import Subscription, StripeSubscription
import stripe
import datetime
from ..stripe.functions import create_customer
import os 

stripe.api_key = os.environ['STRIPE_KEY']

# List view that is used to list current available subscriptions. Can be called by anybody
class SubscriptionsView(ListAPIView):
    permission_classes = (AllowAny, )
    queryset = Subscription.objects.all().exclude(
        name="Default").order_by('priceMonthly')
    serializer_class = SubscriptionSerializer

# View that returns the current subscription that the user is assigned to


class MySubscriptionView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        # Get the current user subscription
        stripe_subscription = StripeSubscription.objects.get(user=user)
        subscription = stripe_subscription.subscription
        serialized_subscription = SubscriptionSerializer(subscription)

        # Get the amount of properties that the agent has used already
        free_property_statuses = get_free_property_statuses()

        # The used properties are all the properties that belong to him with the exclusion of properties that do not count
        used_properties = Property.objects.filter(agent=user.agent).exclude(
            propertyStatus__in=free_property_statuses).count()

        # Create the response and add the remaining values
        response = serialized_subscription.data
        # Add the remaining values
        response['expiryDate'] = stripe_subscription.expiryDate
        # In case we have the free subscription we overwrite the expiry date
        if (subscription.name == 'Free'):
            response['expiryDate'] = datetime.datetime.today() + \
                datetime.timedelta(days=10)
            response['status'] = 'active'
            response['invoiceStatus'] = 'paid'
            response['paymentIntentStatus'] = 'succeeded'
        else:
            response['expiryDate'] = stripe_subscription.expiryDate
            response['status'] = stripe_subscription.status
            response['invoiceStatus'] = stripe_subscription.invoice_status
            response['paymentIntentStatus'] = stripe_subscription.payment_intent_status

        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


""" 
    This view is used so that customers can manage their subscription 
    The view uses the stripe api to generate a portal session
    The portal session needs to be configured in the stripe dashboard and is used to manage the subscriptions
    NOTE: User management should be disabled in the portal as user managaement is performed locally 
"""


class StripePortalView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        # In case the user has not enabled its agent profile and as such he is not stripe customer yet return an unauthorized response
        if (not request.user.stripe_customer_id):
            status_code = status.HTTP_401_UNAUTHORIZED
            response = {'message': "You do'nt have an active account yet."}
            return Response(response, status=status_code)

        session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url='<addWebsiteHere>/pricing',
        )
        status_code = status.HTTP_200_OK
        return Response({"url": session.url}, status=status_code)


""" 
    This view is used so that customers are able to buy subscriptions
    The view uses the stripe api to generate a checkout session
    The checkout seession is then returned to the customer and the frontend redirects the customer to the corresponding checkout
    In the checkout the user can then pay the subscription which redirects him to the success_url
"""


class StripeCheckoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, price_id):
        user = request.user

        # In case the user has not stripe customer id yet then we create the corresponding user
        if (not user.stripe_customer_id):
            customer = create_customer({'email': user.email})
            user.stripe_customer_id = customer['id']
            user.save()

        # Dont allow the user to checkout in case he has a subscription already
        stripe_subscription = StripeSubscription.objects.filter(
            user=request.user)
        # The error should only be shown in case the subscription is not the free subscription
        user_subscription = stripe_subscription[0].subscription
        # ToDo here we need to handle the case when the active subscription is expired (revert to the free subscription?)
        if user_subscription.name != 'Free':
            status_code = status.HTTP_401_UNAUTHORIZED
            response = {
                'message': 'You still have an active subscription.'}
            return Response(response, status=status_code)

        session = stripe.checkout.Session.create(
            success_url='<addWebsiteHere>/pricing/success',
            cancel_url='<addWebsiteHere>/pricing',
            mode='subscription',  # setup a subscription 
            line_items=[{  # the list of items that the user is purchasing 
                'price': price_id,
                # For metered billing, do not pass quantity
                'quantity': 1
            }],
            # ToDo: fields that can be useful for production later on: 
            #    "billing_address_collection": 
            #    "automatic_tax": {
            #        "enabled": true
            #    }
            #    "tax_id_collection": {
            #        "enabled": true
            #    }
            #    "customer_update": {
            #        "address": "auto",
            #        "name": "auto"
            #    }                
            customer=request.user.stripe_customer_id
        )
        status_code = status.HTTP_200_OK
        return Response({"url": session.url}, status=status_code)

# View for the stripe webhooks
# The webhooks are only used by stripe whenever something is changing such as a customer subscribed to a subscription
# Or a payment has failed
# For more about our webhook events check out https://stripe.com/docs/webhooks.


class StripeWebhookView(APIView):
    permission_classes = (AllowAny, )

    # The webhook uses a post request
    def post(self, request):

        webhook_secret = 'whsec_g6zF49t7F7sXwNkl8EIQgEZylEH1D6Fw'

        request_body = request.body
        request_data = request.data

        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('Stripe-Signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request_body, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({'status': 'success'}, status=status_code)

        event_type = event['type']
        data_object = event['data']['object']

        ###########################
        #  Subscription webhooks  #
        ###########################

        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        if event_type == 'customer.subscription.updated':
            # In case of a completed checkout simply update the subscription
            update_subscription_from_webhook(data_object)
            status_code = status.HTTP_200_OK
            return Response({'status': 'success'}, status=status_code)
        elif event_type == 'invoice.paid':
            # In case of a paid invoice we do the same
            update_subscription_from_webhook(data_object)
            status_code = status.HTTP_200_OK
            return Response({'status': 'success'}, status=status_code)
        elif event_type == 'invoice.payment_failed':
            # And update the subscription as well for an invoice payment failed event. This needs to be tested beforehand
            update_subscription_from_webhook(data_object)
            status_code = status.HTTP_200_OK
            return Response({'status': 'success'}, status=status_code)
        elif event_type == 'customer.subscription.deleted':
            update_subscription_from_webhook(data_object)
            status_code = status.HTTP_200_OK
            return Response({'status': 'success'}, status=status_code)
        else:
            print('Unhandled event type {}'.format(event_type))
            status_code = status.HTTP_404_NOT_FOUND
            return Response({'status': 'Unknown event type'}, status=status_code)
