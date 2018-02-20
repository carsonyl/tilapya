"""
Encapsulations of errors from the TransLink API.
"""
from requests.exceptions import HTTPError
from collections import namedtuple


class TransLinkAPIError(HTTPError):
    """
    An error response from the TransLink API.

    :ivar code: API error code. Only applies to the RTTI API.
    :ivar message: Message from the error response.
        Empty if the response body is invalid or empty.
    :ivar request: The request that led to the error response.
    :ivar response: The original response.
    """

    def __init__(self, response):
        blurb = 'HTTP {} Error'.format(response.status_code)

        self.code = ''
        self.message = ''
        try:
            js = response.json()
            blurb += ': '
            self.code = js.get('Code', '')  # Code only in RTTI.
            self.message = js['Message']
            if self.code:
                blurb += 'code {} '.format(self.code)
            blurb += "'{}'".format(self.message)
        except (ValueError, KeyError):
            # Not JSON, as with bad API key for GTFS-RT.
            # Or JSON but without Message.
            pass

        super(TransLinkAPIError, self).__init__(blurb, response=response)

    @property
    def description(self):
        """
        The documented description of the error code, if any.
        """
        return _code_to_desc.get(self.code, '')


ErrorCodeInfo = namedtuple('ErrorCodeInfo', ['code', 'desc'])


class ErrorCodes(object):
    """
    Error codes and documented descriptions for the RTTI API.
    """
    # 1000x: General
    invalid_api_key = ErrorCodeInfo('10001', 'Invalid API key')
    db_error = ErrorCodeInfo('10002', 'Database connection error')

    # 10xx: Stops
    stop_invalid_stop = ErrorCodeInfo('1001', 'Invalid stop number')
    stop_stop_not_found = ErrorCodeInfo('1002', 'Stop number not found')
    stop_unknown_stop_check = ErrorCodeInfo('1003', 'Unknown stop check error')
    stop_unknown_get_stop = ErrorCodeInfo('1004', 'Unknown get stop error')
    stop_invalid_coord = ErrorCodeInfo('1011', 'Invalid latitude/longitude')
    stop_no_stops_found = ErrorCodeInfo('1012', 'No stops found')
    stop_unknown_get = ErrorCodeInfo('1013', 'Unknown get stops error')
    stop_radius_too_large = ErrorCodeInfo('1014', 'Radius too large')
    stop_invalid_route = ErrorCodeInfo('1015', 'Invalid route number')

    # 20xx: Buses
    bus_invalid_bus = ErrorCodeInfo('2001', 'Invalid bus number')
    bus_bus_not_found = ErrorCodeInfo('2002', 'Bus number not found')
    bus_unknown_get_bus = ErrorCodeInfo('2003', 'Unknown get bus error')
    bus_no_buses_found = ErrorCodeInfo('2011', 'No buses found')
    bus_unknown_get_bus_by_stop = ErrorCodeInfo('2012', 'Unknown get buses by stop error')
    bus_unknown_get_bus_by_route = ErrorCodeInfo('2013', 'Unknown get buses by route error')
    bus_invalid_stop = ErrorCodeInfo('2014', 'Invalid stop number')
    bus_invalid_route = ErrorCodeInfo('2015', 'Invalid route number')
    bus_stop_not_found = ErrorCodeInfo('2016', 'Stop number not found')
    bus_route_not_found = ErrorCodeInfo('2017', 'Route number not found')
    bus_unknown_get_bus_by_stop_and_route = ErrorCodeInfo('2018', 'Unknown get buses by stop and route error')

    # 30xx, Stop Estimates
    est_invalid_stop = ErrorCodeInfo('3001', 'Invalid stop number')
    est_stop_not_found = ErrorCodeInfo('3002', 'Stop number not found')
    est_unknown = ErrorCodeInfo('3003', 'Unknown get estimates error')
    est_invalid_route = ErrorCodeInfo('3004', 'Invalid route')
    est_no_estimates = ErrorCodeInfo('3005', 'No stop estimates found')
    est_invalid_time = ErrorCodeInfo('3006', 'Invalid time frame')
    est_invalid_count = ErrorCodeInfo('3007', 'Invalid count')

    # 40xx, Routes
    route_route_not_found = ErrorCodeInfo('4002', 'Route number not found')
    route_unknown_get = ErrorCodeInfo('4003', 'Unknown get route error')
    route_invalid_route = ErrorCodeInfo('4004', 'Invalid route number')
    route_invalid_stop = ErrorCodeInfo('4011', 'Invalid stop number')
    route_stop_not_found = ErrorCodeInfo('4012', 'Stop number not found')
    route_unknown = ErrorCodeInfo('4013', 'Unknown error')
    route_no_routes_found = ErrorCodeInfo('4014', 'No routes found')

    # 500x, Status
    status_invalid_service = ErrorCodeInfo('5001', 'Invalid service name')


_code_to_desc = {v.code: v.desc for v in ErrorCodes.__dict__ if isinstance(v, ErrorCodeInfo)}
