"""
Tilapya wrapper around TransLink's Real-Time Transit Information (RTTI) API.

.. note:: This API is limited to real-time information for buses.
        In addition, some routes and vehicles may not be available.
        Buses that are not in service are not exposed by the API.

.. seealso:: `TransLink's RTTI API reference <https://developer.translink.ca/ServicesRtti/ApiReference>`_.
    Much of it is replicated here for convenience.
    However, the docs here reflect Tilapya-specific behaviour.


Usage examples
--------------

.. code-block:: python
   :caption: Find the name of bus stop 53095, and whether it's wheelchair-accessible.

    >>> from tilapya import RTTI
    >>> api = RTTI('my key')
    >>> stop = api.stop('53095')
    >>> stop.Name
    'WB DOVER ST FS ROYAL OAK AVE'
    >>> stop.WheelchairAccess
    False

.. code-block:: python
   :caption: Get all the route map KML links for bus route 324.

    >>> route = api.route('324')
    >>> [pattern.RouteMap.Href for pattern in route.Patterns]
    ['http://nb.translink.ca/geodata/trip/324-NB1.kmz', 'http://nb.translink.ca/geodata/trip/324-NB1L.kmz', 'http://nb.translink.ca/geodata/trip/324-SB1.kmz']

.. code-block:: python
   :caption: Find the last reported route and position of bus 2543.

    >>> bus = api.bus('2543')
    >>> f'{bus.RouteNo} {bus.Destination} ({bus.Direction})'
    '020 VICTORIA (SOUTH)'
    >>> bus.Latitude, bus.Longitude
    (49.2805, -123.11725)
    >>> bus.RecordedTime.isoformat()
    '2018-02-19T22:07:57-08:00'

.. code-block:: python
   :caption: Get the next two predicted (or scheduled) arrival times for the 502 bus at bus stop 55070.

    >>> est = api.stop_estimates('55070', count=2, route_number='502')[0]
    >>> [f'{sked.ExpectedLeaveTime.isoformat()} - {est.RouteNo} {sked.Destination}' for sked in est.Schedules]
    ['2018-02-19T22:30:00-08:00 - 502 LANGLEY CTR', '2018-02-19T22:58:00-08:00 - 502 LANGLEY CTR']


"""
from collections import namedtuple
from datetime import datetime, timedelta

from marshmallow import Schema, fields, post_load
from pytz import timezone

from ._util import TransLinkAPIBase


#: TransLink's local time zone (Vancouver).
TRANSLINK_TZ = timezone('America/Vancouver')


class Stop(namedtuple('Stop', [
        'StopNo', 'Name', 'BayNo', 'City', 'OnStreet', 'AtStreet',
        'Latitude', 'Longitude', 'WheelchairAccess', 'Distance', 'Routes'])):
    """
    Stops are locations where buses provide scheduled service.

    :ivar int StopNo: The 5-digit stop number.
    :ivar Name: The stop name.
    :ivar BayNo: The bay number, if applicable.
    :ivar City: The city in which the stop is located.
    :ivar OnStreet: The street name the stop is located on.
    :ivar AtStreet: The intersecting street of the stop.
    :ivar float Latitude: The latitude of the stop.
    :ivar float Longitude: The longitude of the stop.
    :ivar bool WheelchairAccess: Specifies wheelchair accessible stop.
    :ivar Distance: Distance away from the search location.
    :ivar list[Route] Routes: The list of routes that the stop services.
    """


class StopEstimate(namedtuple('StopEstimate', [
        'RouteNo', 'RouteName', 'Direction', 'RouteMap', 'Schedules'])):
    """
    Bus arrival estimates for a route at a stop.

    :ivar RouteNo: The bus route number.
    :ivar RouteName: The bus route name.
    :ivar Direction: The direction of the route at the specific stop.
    :ivar RouteMap RouteMap: The element containing the route map information.
    :ivar list[Schedule] Schedules: The element containing the list of schedules.
    """


class RouteMap(namedtuple('RouteMap', ['Href'])):
    """
    Bus route map.

    :ivar href: The location of the route map file in KMZ format.
    """


class Schedule(namedtuple('Schedule', [
        'Pattern', 'Destination', 'ExpectedLeaveTime', 'ExpectedCountdown',
        'ScheduleStatus', 'CancelledTrip', 'CancelledStop',
        'AddedTrip', 'AddedStop', 'LastUpdate'])):
    """
    A piece of real-time or scheduled arrival time information for a single bus.

    :ivar Pattern: The pattern of the specific trip.
    :ivar Destination: The destination of the trip.
    :ivar datetime ExpectedLeaveTime: The expected departure time of the trip at the specific stop.
        The original value is something like "05:20pm 2018-02-18".
        This is converted to an absolute datetime with time zone.
        Seconds are always 0.
    :ivar int ExpectedCountDown: The expected departure time in minutes.
    :ivar ScheduleStatus: The status of the trip.

        * ``*`` indicates scheduled time
        * ``-`` indicates delay
        * ``+`` indicates bus is running ahead of schedule
    :ivar bool AddedTrip: Indicates if trip is added.
    :ivar bool CancelledTrip: Indicates if trip is cancelled.
    :ivar bool CancelledStop: Indicates if stop is cancelled.
    :ivar bool AddedTrip: 	Indicates if trip is added.
    :ivar bool AddedStop: Indicates if stop is added.
    :ivar datetime LastUpdate: The last updated time of the trip.
        The original value is something like "05:20:30 pm".
        This is converted to an absolute datetime with time zone.
    """


class Bus(namedtuple('Bus', [
        'VehicleNo', 'TripId', 'RouteNo',
        'Direction', 'Destination', 'Pattern',
        'Latitude', 'Longitude', 'RecordedTime', 'RouteMap'])):
    """
    Information about a bus.

    :ivar VehicleNo: The vehicle number of the bus.
    :ivar int TripId: The id of the trip the bus currently running.
    :ivar RouteNo: The route number of the vehicle.
    :ivar Direction: The direction of the trip.
    :ivar Destination: The destination headsign of the trip.
        *This field is not in the RTTI API documentation.*
    :ivar Pattern: The pattern of the trip.
    :ivar float Latitude: The latitude of the vehicle location.
    :ivar float Longitude: The longitude of the vehicle location.
    :ivar datetime RecordedTime: The recorded time of the last location of the vehicle.
        The original value is something like "05:20:30 pm".
        This is converted to an absolute datetime with time zone.
    :ivar RouteMap RouteMap: The element containing the route map information.
    """


class Route(namedtuple('Route', ['RouteNo', 'Name', 'OperatingCompany', 'Patterns'])):
    """
    Routes are a sequenced pattern of service.

    :ivar RouteNo: The bus route number.
    :ivar Name: The name of the route.
    :ivar OperatingCompany: The operating company of the route.
    :ivar list[Pattern] patterns: The list of patterns for the route.
    """


class Pattern(namedtuple('Pattern', ['PatternNo', 'Destination', 'RouteMap', 'Direction'])):
    """
    A route trip pattern.

    :ivar PatternNo: The pattern number.
    :ivar Destination: The destination of the pattern.
    :ivar RouteMap RouteMap: The element containing the route map information.
    :ivar Direction: The direction of the pattern.
    """


class Status(namedtuple('Status', ['Name', 'Value'])):
    """
    Status info for a service within the RTTI API.

    :ivar name: The name of the service ("Location" or "Schedule")
    :ivar value: The status of the service ("Online" or "Offline")
    """


class StopSchema(Schema):
    StopNo = fields.Integer(required=True)
    Name = fields.String(required=True)
    BayNo = fields.String(required=True)
    City = fields.String(required=True)
    OnStreet = fields.String(required=True)
    AtStreet = fields.String(required=True)
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
    WheelchairAccess = fields.Boolean(required=True)
    Distance = fields.Integer(required=True)
    Routes = fields.String(required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Stop(**js)


def parse_leave_time(value, relative_to=None):
    # Assumes English locale.
    try:
        return TRANSLINK_TZ.localize(datetime.strptime(value, '%I:%M%p %Y-%m-%d'))
    except ValueError:
        if not relative_to:
            relative_to = datetime.now(TRANSLINK_TZ)
        parsed = TRANSLINK_TZ.localize(datetime.strptime(value, '%I:%M%p'))
        parsed = relative_to.replace(
            hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
        # Time has no date? Assume it's for tomorrow.
        parsed += timedelta(days=1)
        return parsed


def parse_last_update(value, relative_to=None):
    # Assumes English locale.
    if not relative_to:
        relative_to = datetime.now(TRANSLINK_TZ)
    parsed = datetime.strptime(value, '%I:%M:%S %p')
    parsed = relative_to.replace(
        hour=parsed.hour, minute=parsed.minute, second=parsed.second, microsecond=0)
    if parsed > relative_to:
        parsed -= timedelta(days=1)
    return parsed


class ScheduleSchema(Schema):
    Pattern = fields.String(required=True)
    Destination = fields.String(required=True)
    ExpectedLeaveTime = fields.Function(
        deserialize=parse_leave_time, required=True)
    ExpectedCountdown = fields.Integer(required=True)
    ScheduleStatus = fields.String(required=True)
    CancelledTrip = fields.Boolean(required=True)
    CancelledStop = fields.Boolean(required=True)
    AddedTrip = fields.Boolean(required=True)
    AddedStop = fields.Boolean(required=True)
    LastUpdate = fields.Function(deserialize=parse_last_update, required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Schedule(**js)


class RouteMapSchema(Schema):
    Href = fields.Url(relative=False, required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return RouteMap(**js)


class StopEstimateSchema(Schema):
    RouteNo = fields.String(required=True)
    RouteName = fields.String(required=True)
    Direction = fields.String(required=True)
    RouteMap = fields.Nested(RouteMapSchema, many=False, required=True)
    Schedules = fields.Nested(ScheduleSchema, many=True, required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return StopEstimate(**js)


class BusSchema(Schema):
    VehicleNo = fields.String(required=True)
    TripId = fields.Integer(required=True)
    RouteNo = fields.String(required=True)
    Direction = fields.String(required=True)
    Destination = fields.String(required=True)
    Pattern = fields.String(required=True)
    Latitude = fields.Float(required=True)
    Longitude = fields.Float(required=True)
    RecordedTime = fields.Function(deserialize=parse_last_update, required=True)
    RouteMap = fields.Nested(RouteMapSchema, many=False, required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Bus(**js)


class PatternSchema(Schema):
    PatternNo = fields.String(required=True)
    Destination = fields.String(required=True)
    RouteMap = fields.Nested(RouteMapSchema, many=False, required=True)
    Direction = fields.String(required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Pattern(**js)


class RouteSchema(Schema):
    RouteNo = fields.String(required=True)
    Name = fields.String(required=True)
    OperatingCompany = fields.String(required=True)
    Patterns = fields.Nested(PatternSchema, many=True, required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Route(**js)


class StatusSchema(Schema):
    Name = fields.String(required=True)
    Value = fields.String(required=True)

    @post_load
    def make_obj(self, js, **kwargs):
        return Status(**js)


class RTTI(TransLinkAPIBase):
    """
    The wrapper around TransLink's Real-Time Transit Information (RTTI) API.
    """

    def __init__(self, api_key, session=None):
        """
        :param api_key: TransLink API key.
        :param requests.Session session: Session to use, instead of the default.
        """
        super(RTTI, self).__init__(
            'https://api.translink.ca/rttiapi/v1/',
            api_key=api_key, session=session)

    def stop(self, stop_number):
        """
        Get a bus stop by bus stop number.

        :param stop_number: 5-digit bus stop number.
        :rtype: Stop
        """
        return self._get_deserialized('stops/{}'.format(stop_number), StopSchema())

    def _stops(self, **kwargs):
        return self._get_deserialized('stops', StopSchema(many=True), params=kwargs)

    def stops(self, lat, long, radius_m=None, route_number=None):
        """
        Search for stops around a certain point.

        :param float lat: Latitude.
        :param float long: Longitude.
        :param int radius_m: Search this radius for stops. Default 500. Maximum 2000.
        :param route_number: Search for stops served by this route.
        :rtype: list[Stop]
        """
        return self._stops(
            lat='{:.6f}'.format(lat), long='{:.6f}'.format(long),
            radius=radius_m, routeno=route_number)

    def stop_estimates(self, stop_number, count=None, timeframe=None, route_number=None):
        """
        Gets the next bus estimates for a particular stop. Returns schedule data if estimates are not available.

        :param stop_number: A five-digit stop number.
        :param int count: The number of buses to return. Default 6.
        :param int timeframe: The search time frame in minutes. Default 120.
        :param route_number: If present, will search for stops specific to route.
        :returns: A list of :class:`StopEstimate`. Appears to be grouped by
            route, destination, and direction (not documented).
        :rtype: list[StopEstimate]
        """
        return self._get_deserialized(
            'stops/{}/estimates'.format(stop_number),
            StopEstimateSchema(many=True),
            params={'count': count, 'timeframe': timeframe, 'routeNo': route_number})

    def bus(self, bus_number):
        """
        Get a bus by its bus vehicle number.

        :param bus_number: A vehicle id.
            It is not possible to get a bus that is not currently in service.

            .. note:: This endpoint erroneously rejects 5-digit bus numbers.
        :rtype: Bus
        """
        return self._get_deserialized('buses/{}'.format(bus_number), BusSchema(many=False))

    def buses(self, stop_number=None, route_number=None):
        """
        Retrieve vehicle information of all or a filtered set of buses.

        :param stop_number: If present, will search for buses for stop id specified.
        :param route_number: If present, will search for stops specific to route.
        :rtype: list[Bus]
        """
        return self._get_deserialized(
            'buses', BusSchema(many=True),
            params={'stopNo': stop_number, 'routeNo': route_number})

    def route(self, route_number):
        """
        Get a route by its route number.

        :param route_number: A bus route number.
        :rtype: Route
        """
        return self._get_deserialized(
            'routes/{}'.format(route_number), RouteSchema(many=False))

    def routes(self, stop_number=None):
        """
        Get routes.

        .. note:: This endpoint may intermittently and incorrectly return
            error code 4014 (no routes for specified stop).

        :param stop_number: If present, will search for routes passing through this stop.

            .. note:: Though it's implied that leaving this unspecified will return all routes,
                in practice, this parameter is required.
        :rtype: list[Route]
        """
        return self._get_deserialized(
            'routes', RouteSchema(many=True), params={'stopNo': stop_number})

    def status(self, service='all'):
        """
        Gets the bus location and real-time schedule information update status.

        :param service: A service name.

            * ``location`` for bus location information,
            * ``schedule`` for real-time schedule information
            * ``all`` for both services
        :rtype: list[Status]
        """
        return self._get_deserialized('status/{}'.format(service), StatusSchema(many=True))
