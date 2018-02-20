from datetime import datetime

import pytest
from requests import codes

from tilapya.errors import TransLinkAPIError
from tilapya.errors import ErrorCodes as EC
from tilapya.rtti import (RTTI, TRANSLINK_TZ, parse_last_update,
                          parse_leave_time)


# Apply VCR to all tests in this file.
pytestmark = pytest.mark.vcr

TS_FORMAT = '%Y-%m-%d %H:%M:%S'


@pytest.fixture
def authed_rtti(valid_api_key):
    return RTTI(api_key=valid_api_key)


@pytest.mark.parametrize('value,relative_to,expected', [
    ['9:59pm 2018-02-13', '2018-02-13 21:30:00', '2018-02-13 21:59:00'],
    ['12:09am', '2018-02-13 23:00:00', '2018-02-14 00:09:00'],
    ['10:00pm', '2018-02-13 23:00:00', '2018-02-14 22:00:00'],  # Not ideal.
])
def test_parse_leave_time(value, relative_to, expected):
    relative_to = TRANSLINK_TZ.localize(datetime.strptime(relative_to, TS_FORMAT))
    parsed = parse_leave_time(value, relative_to)
    assert parsed == TRANSLINK_TZ.localize(datetime.strptime(expected, TS_FORMAT))


@pytest.mark.parametrize('value,relative_to,expected', [
    ['08:53:10 pm', '2018-01-01 21:00:00', '2018-01-01 20:53:10'],
    ['08:53:10 pm', '2018-01-02 00:30:00', '2018-01-01 20:53:10'],
    ['01:00:00 am', '2018-01-02 00:30:00', '2018-01-01 01:00:00'],
])
def test_parse_last_update(value, relative_to, expected):
    relative_to = TRANSLINK_TZ.localize(datetime.strptime(relative_to, TS_FORMAT))
    parsed = parse_last_update(value, relative_to)
    assert parsed == TRANSLINK_TZ.localize(datetime.strptime(expected, TS_FORMAT))
    assert parsed.isoformat().endswith('-08:00') or parsed.isoformat().endswith('-07:00')


def test_stop_identity(authed_rtti):
    stop = authed_rtti.stop('53095')
    assert stop.StopNo == 53095


@pytest.mark.parametrize('lat,long,radius,route', [
    [49.248523999, -123.108800, None, None],
    [49.248523999, -123.108800, 500, None],
    [49.248523999, -123.108800, None, 'N15'],
    [49.248523999, -123.108800, 500, 'N15'],
])
def test_stops_with_results(authed_rtti, lat, long, radius, route):
    stops = authed_rtti.stops(lat=lat, long=long, radius_m=radius, route_number=route)
    assert len(stops) > 0


@pytest.mark.parametrize('stop,expect_code', [
    ['00000', EC.stop_stop_not_found],
    ['ABC', EC.stop_invalid_stop],
])
def test_stop_errors(authed_rtti, stop, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.stop(stop)
    assert info.value.code == expect_code.code


@pytest.mark.parametrize('lat,long,radius,route,expect_code', [
    [0, 0, None, None, EC.stop_no_stops_found],
    [999, 999, None, None, EC.stop_invalid_coord],
    [49.1, -123.2, None, None, EC.stop_no_stops_found],
    [49.187706, -122.850060, 9001, None, EC.stop_radius_too_large],
    [49.187706, -122.850060, None, '999', EC.stop_no_stops_found],
    [49.187706, -122.850060, None, 'ABC', EC.stop_invalid_route],
])
def test_stops_errors(authed_rtti, lat, long, radius, route, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.stops(lat=lat, long=long, radius_m=radius, route_number=route)
    assert info.value.code == expect_code.code


@pytest.mark.parametrize('stop,count,timeframe,route', [
    ['60980', None, None, None],
    ['60980', 3, None, None],
    ['60980', None, 120, None],
    ['60980', 3, 120, '050'],
])
def test_stop_estimates_with_results(authed_rtti, stop, count, timeframe, route):
    estimates = authed_rtti.stop_estimates(
        stop, count=count, timeframe=timeframe, route_number=route)
    assert estimates
    if route:
        assert [route] == list(map(lambda est: est.RouteNo, estimates))


@pytest.mark.parametrize('stop,count,timeframe,route,expect_code', [
    ['53095', 0, None, None, EC.est_invalid_count],
    ['53095', None, 0, None, EC.est_invalid_time],
    ['53095', None, None, 'ABC', EC.est_invalid_route],
    ['53095', None, None, '99', EC.est_no_estimates],
    ['ABC', None, None, None, EC.est_invalid_stop],
    ['00000', None, None, None, EC.est_stop_not_found],
])
def test_stop_estimates_errors(authed_rtti, stop, count, timeframe, route, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.stop_estimates(
            stop, count=count, timeframe=timeframe, route_number=route)
    assert info.value.code == expect_code.code


def test_get_buses(authed_rtti):
    all_buses = authed_rtti.buses()
    assert len(all_buses) > 0

    # BUG: 5 digit bus numbers are real, but we can't ask RTTI API for one.
    buses_with_usable_id = filter(lambda b: len(b.VehicleNo) <= 4, all_buses)
    arbitrary_first_bus = next(buses_with_usable_id)

    bus = authed_rtti.bus(arbitrary_first_bus.VehicleNo)
    assert bus.VehicleNo == arbitrary_first_bus.VehicleNo


@pytest.mark.xfail(reason='RTTI API erroneously rejects 5-digit vehicle numbers')
def test_get_5_digit_bus(authed_rtti):
    long_buses = filter(lambda b: len(b.VehicleNo) > 4, authed_rtti.buses())
    authed_rtti.bus(next(long_buses).VehicleNo)


@pytest.mark.parametrize('bus,expect_code', [
    ['0', EC.bus_invalid_bus],
    ['1234', EC.bus_bus_not_found],
])
def test_bus_errors(authed_rtti, bus, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.bus(bus)
    assert info.value.code == expect_code.code


@pytest.mark.parametrize('route,stop', [
    [228, 53987],
    ['228', '53987'],
    ['228', None],
    [None, '53987'],
])
def test_get_buses_with_filter(authed_rtti, route, stop):
    buses = authed_rtti.buses(route_number=route, stop_number=stop)
    assert len(buses) > 0


@pytest.mark.parametrize('route,stop,expect_code', [
    ['ABC', None, EC.bus_invalid_route],
    ['001', None, EC.bus_invalid_route],
    # TODO: Find example of 'route not found' error.
    # ['90', None, EC.bus_route_not_found],
    [None, 'ABC', EC.bus_invalid_stop],
    [None, '12345', EC.bus_stop_not_found],
    ['99', '53095', EC.bus_no_buses_found],
])
def test_get_buses_errors(authed_rtti, route, stop, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.buses(stop_number=stop, route_number=route)
    assert info.value.code == expect_code.code


@pytest.mark.parametrize('route_number,expect_route_number', [
    ('2', '002'),
    ('02', '002'),
    ('144', '144'),
    ('N9', 'N9'),
    ('C2', 'C2'),
])
def test_route(authed_rtti, route_number, expect_route_number):
    route = authed_rtti.route(route_number)
    assert route.RouteNo == expect_route_number


@pytest.mark.parametrize('route,expect_code', [
    ['0', EC.route_invalid_route],
    # TODO: Find example of 'route not found'.
    # ['1', EC.route_route_not_found],
    ['1', EC.route_invalid_route],
    ['N', EC.route_invalid_route],
    ['N0', EC.route_invalid_route],
    ['N09', EC.route_invalid_route],
    ['N1', EC.route_invalid_route],
    ['Q1', EC.route_invalid_route],
])
def test_route_error_codes(authed_rtti, route, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.route(route)
    assert info.value.code == expect_code.code


@pytest.mark.parametrize('stop', [
    '53095',  # API sometimes lies and returns an error for this stop.
    '55385',
])
def test_routes(authed_rtti, stop):
    routes = authed_rtti.routes(stop_number=stop)
    assert len(routes) > 0


@pytest.mark.parametrize('stop,expect_code', [
    ['ABCDE', EC.route_invalid_stop],
    ['00000', EC.route_stop_not_found],
    ['90000', EC.route_stop_not_found],
    # TODO: Real stop that has no routes.
])
def test_routes_error_codes(authed_rtti, stop, expect_code):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.routes(stop)
    assert info.value.code == expect_code.code


@pytest.mark.xfail(reason='Always a database error when RTTI API asked for all routes, contrary to doc')
def test_all_routes(authed_rtti):
    routes = authed_rtti.routes()
    assert len(routes) > 0


@pytest.mark.parametrize('service', ['all', 'location', 'schedule'])
def test_status(authed_rtti, service):
    assert authed_rtti.status(service)


def test_status_error_code(authed_rtti):
    with pytest.raises(TransLinkAPIError) as info:
        authed_rtti.status('foo')
    assert info.value.code == EC.status_invalid_service.code


@pytest.mark.parametrize('key', ['foobar', 'x' * 20])
def test_rtti_ad_key(key):
    # Same message regardless of key length.
    with pytest.raises(TransLinkAPIError) as info:
        RTTI(api_key=key).route('144')
    assert info.value.response.status_code == codes.server_error  # It's never 403.
    assert info.value.code == EC.invalid_api_key.code
    assert info.value.message
