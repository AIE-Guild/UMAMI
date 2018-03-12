# -*- coding: utf-8 -*-
import pytest
from django.core.validators import ValidationError

from redirect.models import Redirect, URLPathValidator

def test_validator():
    validator = URLPathValidator()
    assert validator('test') is None
    assert validator('/test') is None
    assert validator('/test/foo') is None
    assert validator('/test/foo=bar') is None
    with pytest.raises(ValidationError):
        validator('test?foo=bar')
    with pytest.raises(ValidationError):
        validator('/test?foo=bar')
    with pytest.raises(ValidationError):
        validator('/test/foo;bar;baz')

def test_path():
    redirect = Redirect.objects.create(path='test', location='https://www.example.com')
    assert redirect.path == '/test'
    redirect = Redirect.objects.create(path='/test2', location='https://www.example.com')
    assert redirect.path == '/test2'
    with pytest.raises(ValidationError):
        redirect = Redirect(path='test3?foo=bar', location='https://www.example.com')
        redirect.full_clean()

def test_location():
    redirect = Redirect.objects.create(path='test', location='https://www.example.com')
    assert redirect.location == 'https://www.example.com'

def test_url(settings):
    settings.REDIRECT_HOST = 'www.foo.com'
    settings.REDIRECT_SECURE = True
    redirect = Redirect(path='/test', location='https://www.example.com')
    assert redirect.url == 'https://www.foo.com/test'

    settings.REDIRECT_HOST = 'www.foo.com'
    settings.REDIRECT_SECURE = False
    redirect = Redirect(path='/test', location='https://www.example.com')
    assert redirect.url == 'http://www.foo.com/test'

