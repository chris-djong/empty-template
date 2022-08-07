from django.conf.urls import url 
from django.urls import path
from . import views
 
urlpatterns = [ 
            url(r'^api/subscriptions', views.SubscriptionsView.as_view()),
            url(r'^api/subscription', views.MySubscriptionView.as_view()),
            url(r'^api/stripe/webhook', views.StripeWebhookView.as_view()),
            url(r'^api/stripe/checkout/(?P<price_id>[0-9A-z]+)', views.StripeCheckoutView.as_view()),
            url(r'^api/stripe/portal', views.StripePortalView.as_view()),
            ]

