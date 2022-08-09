from api.stripe.models import Subscription

Subscription.objects.create(name='Default', description='The default subscription for each initial user', priceMonthly=0, priceYearly=0)