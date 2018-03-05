import pytest
from requests import codes

from tilapya.errors import TransLinkAPIError
from tilapya.gtfsrt import GTFSRT
from .conftest import remove_response_headers_func


# Apply VCR to all tests in this file.
pytestmark = pytest.mark.vcr(before_record_response=remove_response_headers_func('Set-Cookie'))


@pytest.fixture
def authed_gtfs(valid_api_key):
    return GTFSRT(api_key=valid_api_key)


def test_download_realtime(authed_gtfs):
    assert authed_gtfs.trip_updates().content


def test_download_position(authed_gtfs):
    assert authed_gtfs.position().content


def test_gtfsrt_invalid_key():
    with pytest.raises(TransLinkAPIError) as info:
        GTFSRT(api_key='foobar').trip_updates()
    assert info.value.response.status_code == codes.forbidden
    assert not info.value.code
    assert not info.value.message
