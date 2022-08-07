
from django.conf.urls import url 
from api.chat import views 
 
urlpatterns = [ 
            url(r'^api/chat/messages/(?P<id>[0-9a-u-]+)$', views.MessagesByUserIdView.as_view()), # user more letters here as the identifier can start with user- as well 
            url(r'^api/chat/conversations$', views.ConversationsView.as_view()),
            url(r'^api/chat/unread$', views.UnreadConversationsView.as_view()),
            ]
