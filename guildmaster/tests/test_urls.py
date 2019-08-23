from django.urls import reverse


def test_authorization_url():
    url = reverse('guildmaster:authorization', kwargs={'client_name': 'test'})
    assert url.endswith('/ext/auth/test')


def test_token_url():
    url = reverse('guildmaster:token', kwargs={'client_name': 'test'})
    assert url.endswith('/ext/token/test')
