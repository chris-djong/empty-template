from django.conf.urls import url 
from . import views
 
urlpatterns = [ 
            url(r'^api/email-verification', views.VerifyEmailView.as_view()),
            url(r'^api/subscribeNewsletter', views.SubscribeNewsletterView.as_view())
            ]
