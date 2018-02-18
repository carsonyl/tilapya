from collections import namedtuple
from datetime import datetime, timedelta

from marshmallow import Schema, fields, post_load
from pytz import timezone

from ._util import TransLinkAPIBase


TRANSLINK_TZ = timezone('America/Vancouver')

Stop = namedtuple('Stop', [
    'StopNo', 'Name', 'BayNo', 'City', 'OnStreet', 'AtStreet',
    'Latitude', 'Longitude', 'WheelchairAccess', 'Distance', 'Routes',
])
StopEstimate = namedtuple('StopEstimate', [
    'RouteNo', 'RouteName', 'Direction', 'RouteMap', 'Schedules',
])
RouteMap = namedtuple('RouteMap', ['Href'])
Schedule = namedtuple('Schedule', [
    'Pattern', 'Destination', 'ExpectedLeaveTime', 'ExpectedCountdown',
    'ScheduleStatus', 'CancelledTrip', 'CancelledStop',
    'AddedTrip', 'AddedStop', 'LastUpdate',
])
Bus = namedtuple('Bus', [
    'VehicleNo', 'TripId', 'RouteNo',
    'Direction', 'Destination', 'Pattern',
    'Latitude', 'Longitude', 'RecordedTime', 'RouteMap',
])
Route = namedtuple('Route', ['RouteNo', 'Name', 'OperatingCompany', 'Patterns'])
Pattern = namedtuple('Pattern', ['PatternNo', 'Destination', 'RouteMap', 'Direction'])
Status = namedtuple('Status', ['Name', 'Value'])


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
    def make_obj(self, js):
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
            hour=parsed.hour, minute=parsed.minute, second=0)
        # Time has no date? Assume it's for tomorrow.
        parsed += timedelta(days=1)
        return parsed


def parse_last_update(value, relative_to=None):
    # Assumes English locale.
    if not relative_to:
        relative_to = datetime.now(TRANSLINK_TZ)
    parsed = datetime.strptime(value, '%I:%M:%S %p')
    parsed = relative_to.replace(
        hour=parsed.hour, minute=parsed.minute, second=parsed.second)
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
    def make_obj(self, js):
        return Schedule(**js)


class RouteMapSchema(Schema):
    Href = fields.Url(relative=False, required=True)

    @post_load
    def make_obj(self, js):
        return RouteMap(**js)


class StopEstimateSchema(Schema):
    RouteNo = fields.String(required=True)
    RouteName = fields.String(required=True)
    Direction = fields.String(required=True)
    RouteMap = fields.Nested(RouteMapSchema, many=False, required=True)
    Schedules = fields.Nested(ScheduleSchema, many=True, required=True)

    @post_load
    def make_obj(self, js):
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
    def make_obj(self, js):
        return Bus(**js)


class PatternSchema(Schema):
    PatternNo = fields.String(required=True)
    Destination = fields.String(required=True)
    RouteMap = fields.Nested(RouteMapSchema, many=False, required=True)
    Direction = fields.String(required=True)

    @post_load
    def make_obj(self, js):
        return Pattern(**js)


class RouteSchema(Schema):
    RouteNo = fields.String(required=True)
    Name = fields.String(required=True)
    OperatingCompany = fields.String(required=True)
    Patterns = fields.Nested(PatternSchema, many=True, required=True)

    @post_load
    def make_obj(self, js):
        return Route(**js)


class StatusSchema(Schema):
    Name = fields.String(required=True)
    Value = fields.String(required=True)

    @post_load
    def make_obj(self, js):
        return Status(**js)


class RTTI(TransLinkAPIBase):
    """
    TransLink's Real-Time Transit Information API.
    """

    def __init__(self, api_key, session=None):
        super(RTTI, self).__init__(
            'https://api.translink.ca/rttiapi/v1/',
            api_key=api_key, session=session)

    def stop(self, stop_number):
        return self._get_deserialized('stops/{}'.format(stop_number), StopSchema())

    def _stops(self, **kwargs):
        return self._get_deserialized('stops', StopSchema(many=True), params=kwargs)

    def stops(self, lat, long, radius_m=None, route_number=None):
        return self._stops(
            lat='{:.6f}'.format(lat), long='{:.6f}'.format(long),
            radius=radius_m, routeno=route_number)

    def stop_estimates(self, stop_number, count=None, timeframe=None, route_number=None):
        return self._get_deserialized(
            'stops/{}/estimates'.format(stop_number),
            StopEstimateSchema(many=True),
            params={'count': count, 'timeframe': timeframe, 'routeNo': route_number})

    def bus(self, bus_number):
        return self._get_deserialized('buses/{}'.format(bus_number), BusSchema(many=False))

    def buses(self, stop_number=None, route_number=None):
        return self._get_deserialized(
            'buses', BusSchema(many=True),
            params={'stopNo': stop_number, 'routeNo': route_number})

    def route(self, route_number):
        return self._get_deserialized(
            'routes/{}'.format(route_number), RouteSchema(many=False))

    def routes(self, stop_number=None):
        return self._get_deserialized(
            'routes', RouteSchema(many=True), params={'stopNo': stop_number})

    def status(self, service='all'):
        return self._get_deserialized('status/{}'.format(service), StatusSchema(many=True))
