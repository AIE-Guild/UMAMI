from django.urls import path

from guildmaster import views

app_name = 'guildmaster'
urlpatterns = [
    path('auth/<slug:client_name>', views.AuthorizationView.as_view(), name='authorization'),
    path('token/<slug:client_name>', views.TokenView.as_view(), name='token'),
    path('discord/accounts', views.DiscordAccountList.as_view(), name='discord-list'),
    path('discord/accounts/add', views.DiscordAccountAdd.as_view(), name='discord-add'),
]
