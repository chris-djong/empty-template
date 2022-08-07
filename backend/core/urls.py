"""immolux URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('api.properties.urls')),
    url(r'^', include('api.propertyMonitor.urls')),
    url(r'^', include('api.documents.urls')),
    url(r'^', include('api.locations.urls')),
    url(r'^', include('api.users.urls')),    
    url(r'^', include('api.scheduler.urls')),
    url(r'^', include('api.chat.urls')),
    url(r'^', include('api.emails.urls')),
    url(r'^', include('api.stripe.urls')),
    url(r'^', include('api.questions.urls')),
    url(r'^', include('api.locationData.urls')),
    url(r'^', include('api.settings.urls'))
]