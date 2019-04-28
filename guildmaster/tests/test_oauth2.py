def test_get_authorization_url(tf_client, rf, settings):
    request = rf.get('/')
    url = tf_client.get_authorization_url(request)
    assert url.startswith(tf_client.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.GUILDMASTER_SESSION_STATE_KEY]}" in url
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == settings.GUILDMASTER_RETURN_URL

    url = tf_client.get_authorization_url(request, return_url='/foo')
    assert url.startswith(tf_client.authorization_url)
    assert 'response_type=code' in url
    assert f'client_id={tf_client.client_id}' in url
    assert f"state={request.session[settings.GUILDMASTER_SESSION_STATE_KEY]}" in url
    assert request.session[settings.GUILDMASTER_SESSION_RETURN_KEY] == '/foo'
