from django.urls import reverse


def test_authorization_url():
    url = reverse('oauth2:authorization')
    assert url.endswith('/authorization')


def test_token_url():
    url = reverse('oauth2:token')
    assert url.endswith('/token')
