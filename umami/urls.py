# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from umami import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
