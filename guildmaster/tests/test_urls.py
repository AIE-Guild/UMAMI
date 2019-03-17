from django.urls import reverse


def test_authorization_url():
    url = reverse('guildmaster:authorize', kwargs={'client_name': 'test'})
    assert url.endswith('/authorize/test')


def test_token_url():
    url = reverse('guildmaster:token', kwargs={'client_name': 'test'})
    assert url.endswith('/token/test')
