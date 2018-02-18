import imghdr
from datetime import datetime

import pytest

from tilapia.errors import TransLinkAPIError
from tilapia.rtds import RTDS
from requests import codes


@pytest.fixture
def authed_rtds(valid_api_key):
    return RTDS(api_key=valid_api_key)


def test_tile(authed_rtds, tmpdir):
    dest = tmpdir.join('test.png')
    assert authed_rtds.tile(dest, 647, 1402, 12, types=6)
    assert imghdr.what(dest) == 'png'


def test_live_data_timestamp(authed_rtds):
    result = authed_rtds.live_data_timestamp()
    assert isinstance(result.timestampUtc, datetime)


def test_all_live_data(authed_rtds):
    result = authed_rtds.all_live_data()
    assert isinstance(result.timestampUtc, datetime)


def test_live_data_at_point_timestamp(authed_rtds):
    result = authed_rtds.live_data_at_point(
        -123.04550170898438, 49.23194729854554, z=12, types=6)
    assert isinstance(result.timestampUtc, datetime)

    with pytest.raises(TransLinkAPIError) as info:
        authed_rtds.live_data_at_point('abc', -1, z=0, types=-1)
    assert info.value.response.status_code == codes.bad
    assert info.value.message


def test_colour_legend(authed_rtds):
    result = authed_rtds.colour_legend()
    assert isinstance(result, list)


def test_tile_bad_key(tmpdir):
    # Expecting a JSON error response when PNG request is rejected for bad key.
    dest = tmpdir.join('test.png')
    with pytest.raises(TransLinkAPIError) as info:
        RTDS(api_key='foobar').tile(dest, 647, 1402, 12)
    assert info.value.response.status_code == codes.bad
    assert not info.value.code


@pytest.mark.parametrize('key', ['foobar', 'x' * 20])
def test_bad_key(key):
    # There's a different error message for keys that aren't 20 characters.
    with pytest.raises(TransLinkAPIError) as info:
        RTDS(api_key=key).all_live_data()
    assert info.value.response.status_code == codes.bad  # It's never 403.
    assert not info.value.code
    assert info.value.message
