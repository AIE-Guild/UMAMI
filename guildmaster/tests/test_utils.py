import math
import secrets
import datetime as dt

import pytest
from requests.models import Response
import django.utils.timezone

from guildmaster import utils


@pytest.mark.parametrize('n', [32, 64, 128, 256])
def test_generate_state(monkeypatch, settings, n):
    def token(n):
        stream = ('wtW86yurXgPTv8O9IcVclFDY2JBCJZ3wTC6l8TbfimAQrzLfRxNsPjU23'
                  'CKyA1IFu63ddxGgQ0DkNDVgeUpUDGwrgKDIaNbH40p01X5RQVY-agEmfh'
                  'sOqC4epI75h2FIVbopZhzrpGJHrh3heez6jMF1Jjf-T9iVWE1_gIGz2ua'
                  'Y19qkQXqiDCtDdCW4Ha6nlkeaLrnkm5KjZuc1fIOCUh9rzyvqKFMwP-TP'
                  'h5Yz0-_3MFlkRi78G7iiwKoQgf5QtbkELtSXomA6jlh3HJol10CUqLIz3'
                  'nlDVHqr4hc9SC4QVcdbLw6nhZ7Itnk58XzaNS-iLx9xZWzKED0RcOy5RA')
        m = math.ceil(4 * n / 3)
        return stream[:m]

    settings.OAUTH_STATE_BYTES = n
    monkeypatch.setattr(secrets, 'token_urlsafe', token)
    assert utils.generate_state() == token(n)


def test_parse_http_date(mocker):
    response = mocker.Mock(spec=Response)
    response.headers = {'Date': 'Tue, 9 Sep 2001 01:46:40 GMT'}
    assert utils.parse_http_date(response) == 1000000000


def test_parse_http_date_missing(mocker, monkeypatch):
    monkeypatch.setattr(django.utils.timezone, 'now', lambda: dt.datetime.fromtimestamp(1000000000))
    response = mocker.Mock(spec=Response)
    response.headers = {}
    assert utils.parse_http_date(response) == 1000000000
