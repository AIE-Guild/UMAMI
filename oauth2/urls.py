from django.conf import settings
from django.urls import path

from oauth2 import views

app_name = 'oauth2'
urlpatterns = [
    path('authorization/<slug:client_name>', views.AuthorizationView.as_view(), name='authorization'),
    path('token/<slug:client_name>', views.TokenView.as_view(), name='token'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [path('dump', views.ClientDumpView.as_view(), name='dump')]
