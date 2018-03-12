# -*- coding: utf-8 -*-
import pytest

from redirect.models import Redirect
from redirect.middleware import RedirectServiceMiddleware

@pytest.fixture()
def redir():
    return RedirectServiceMiddleware(lambda x: 'spam')

def test_hit(rf, settings, redir):
    settings.REDIRECT_HOST = 'example.com'
    Redirect.objects.create(path='/test', location='https://www.example.org')
    request = rf.get('/test')
    request.META['HTTP_HOST'] = 'example.com'
    response = redir(request)
    assert response.status_code == 302
    assert response['Location'] == 'https://www.example.org'

def test_miss(rf, settings, redir):
    settings.REDIRECT_HOST = 'example.com'
    Redirect.objects.create(path='/test', location='https://www.example.org')
    request = rf.get('/other')
    request.META['HTTP_HOST'] = 'example.com'
    response = redir(request)
    assert response.status_code == 404

def test_nomatch(rf, settings, redir):
    settings.REDIRECT_HOST = 'example.com'
    Redirect.objects.create(path='/test', location='https://www.example.org')
    request = rf.get('/other')
    request.META['HTTP_HOST'] = 'example.org'
    response = redir(request)
    assert response == 'spam'
