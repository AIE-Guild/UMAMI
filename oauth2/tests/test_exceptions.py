from oauth2 import exceptions


def test_oauth2_exception():
    exc = exceptions.OAuth2Error(error='access_denied')
    assert str(exc) == 'access_denied'


def test_oauth2_exception_description():
    exc = exceptions.OAuth2Error(
        error='access_denied', description='The resource owner or authorization server denied the request.'
    )
    assert str(exc) == 'access_denied: The resource owner or authorization server denied the request.'


def test_oauth2_exception_uri():
    exc = exceptions.OAuth2Error(error='access_denied', uri='https://tools.ietf.org/html/rfc6749#section-5.2')
    assert str(exc) == 'access_denied (https://tools.ietf.org/html/rfc6749#section-5.2)'
