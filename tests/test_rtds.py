import pytest
from tilapia.rtds import RTDS
from datetime import datetime
import imghdr


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


def test_colour_legend(authed_rtds):
    result = authed_rtds.colour_legend()
    assert isinstance(result, list)
