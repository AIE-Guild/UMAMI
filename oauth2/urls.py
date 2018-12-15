from django.urls import path

from oauth2 import views

app_name = 'oauth2'
urlpatterns = [
    path('authorization', views.TokenView.as_view(), name='authorization'),
    path('token', views.TokenView.as_view(), name='token')
]
