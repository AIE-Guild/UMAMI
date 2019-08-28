# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture()
def client(client, settings):
    settings.SECURE_SSL_REDIRECT = False
    return client
