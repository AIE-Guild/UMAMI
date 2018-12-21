from django.urls import path

from oauth2 import views

app_name = 'oauth2'
urlpatterns = [
    path('authorization/<slug:client_name>', views.TokenView.as_view(), name='authorization'),
    path('token/<slug:client_name>', views.TokenView.as_view(), name='token')
]
