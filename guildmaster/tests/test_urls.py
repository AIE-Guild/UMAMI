from django.urls import reverse


def test_authorization_url():
    url = reverse('oauth2:authorization', kwargs={'client_name': 'test'})
    assert url.endswith('/authorization/test')


def test_token_url():
    url = reverse('oauth2:token', kwargs={'client_name': 'test'})
    assert url.endswith('/token/test')
