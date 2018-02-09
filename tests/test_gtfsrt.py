import pytest
from tilapia.gtfsrt import GTFSRT
from datetime import datetime


@pytest.fixture
def authed_gtfs(valid_api_key):
    return GTFSRT(api_key=valid_api_key)


def test_headers_realtime(authed_gtfs):
    head = authed_gtfs.headers_realtime()
    assert isinstance(head.date, datetime)
    assert head.content_length > 0
    assert head.content_disposition


def test_download_realtime(authed_gtfs, tmpdir):
    dest = tmpdir.join('gtfsrt.pb')
    assert authed_gtfs.download_realtime(dest)


def test_headers_position(authed_gtfs):
    head = authed_gtfs.headers_position()
    assert isinstance(head.date, datetime)
    assert head.content_length > 0
    assert head.content_disposition


def test_download_position(authed_gtfs, tmpdir):
    dest = tmpdir.join('gtfsposition.pb')
    assert authed_gtfs.download_position(dest)
