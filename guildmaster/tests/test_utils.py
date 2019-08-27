from guildmaster import utils


def test_parse_http_date(tf_datestr, tf_date):
    assert utils.parse_http_date(tf_datestr) == tf_date
