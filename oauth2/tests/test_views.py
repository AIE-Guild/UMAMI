from django.urls import reverse

from oauth2 import views


def test_authorization(rf):
    request = rf.get(reverse('oauth2:authorization'))
    response = views.AuthorizationView.as_view()(request)
    assert response.status_code == 302


def test_token(rf):
    request = rf.get(reverse('oauth2:token'))
    response = views.TokenView.as_view()(request)
    assert response.status_code == 302
