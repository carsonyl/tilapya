from datetime import datetime

import pytest
from requests import codes

from tilapia.errors import TransLinkAPIError
from tilapia.gtfsrt import GTFSRT
from .conftest import remove_response_headers_func


# Apply VCR to all tests in this file.
pytestmark = pytest.mark.vcr(before_record_response=remove_response_headers_func('Set-Cookie'))


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


def test_gtfsrt_invalid_key():
    with pytest.raises(TransLinkAPIError) as info:
        GTFSRT(api_key='foobar').headers_realtime()
    assert info.value.response.status_code == codes.forbidden
    assert not info.value.code
    assert not info.value.message
