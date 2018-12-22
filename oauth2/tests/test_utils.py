from oauth2 import utils


def test_parse_http_date(sample_datestr, sample_date):
    assert utils.parse_http_date(sample_datestr) == sample_date
