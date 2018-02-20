"""
The Regional Traffic Data System (RTDS) Open API provides services that allow the
users to view and query regional traffic flow information. The system generates two types of data:

1. Real-time traffic data in the form of speed profiles; and
2. Travel time by corridor and roadway segment

The coverage of the RTDS includes provincial highways,
the Major Road Network (MRN) and select arterial roads within the Metro Vancouver boundary as well as
Highway-1 to Chilliwack and Highway-99 to Whistler.

.. seealso:: `TransLink's RTDS API reference <https://developer.translink.ca/Services/ApiReference>`_.
    Much of it is replicated here for convenience.
    However, the docs here reflect Tilapia-specific behaviour.
"""
from ._util import TransLinkAPIBase
from marshmallow import Schema, fields, post_load
from collections import namedtuple


class LiveDataTimestampResult(namedtuple('LiveDataTimestampResult', ['timestampUtc'])):
    """
    Value returned when the user asks for the live data timestamp.

    :ivar datetime.datetime timestampUtc: The timestamp of live data, in UTC time.
        ``None`` if there is no current data.
    """


class LiveDataResult(namedtuple('LiveDataResult', ['timestampUtc', 'data'])):
    """
    Value returned when the user asks for all live data.

    :ivar datetime.datetime timestampUtc: The timestamp of the returned data, in UTC time.
        ``None`` if there is no current data.
    :ivar list[LinkInfo] data: The information for all drivable directions on all links.
    """


class LinkInfo(namedtuple('LinkInfo', [
        'linkId', 'isFwd', 'angle', 'lengthMetres', 'speedKmph', 'travelTimeMinutes', 'quality'])):
    """
    Current information about a direction of travel along a link.

    :ivar int linkId: The ID of the link to which this information applies.
    :ivar bool isFwd: Whether this information applies in the forward (as opposed to reverse) direction of the link.
    :ivar float angle: The angle of travel over the link, in degrees clockwise from North.
        A number between 0.0 and 360.0.
    :ivar float lengthMetres: he length of the link, in metres.
    :ivar float speedKmph: The current speed of the link, in km/h.
        ``None`` if there is no current data for the link.
    :ivar int travelTimeMinutes: The time required to travel the length of the link at current speed, in minutes.
        ``None`` if there is no current data for the link.
    :ivar int quality: The quality of this information, as a value between 0 and 100.
        ``None`` if there is no current data for the link.
    """


class LiveDataAtPointResult(namedtuple('LiveDataAtPointResult', ['x', 'y', 'timestampUtc', 'data'])):
    """
    Value returned when the user asks for live data at a point.

    :ivar float x: The x-coordinate of the point at which this information applies.
    :ivar float y: The y-coordinate of the point at which this information applies.
    :ivar datetime.datetime timestampUtc: The timestamp of the returned data, in UTC time.
        ``None`` if there is no current data.
    :ivar list[LinkInfo] data: The information for all directions that apply at this point.
    """


class ColourLegendItem(namedtuple('ColourLegendItem', ['name', 'colour'])):
    """
    Entry in the legend that describes the colours used by the map tiles.

    :ivar name: The speed category name for this category. One of 'Fast', 'Medium', 'Slow', or 'Unknown'.
    :ivar colour: A web-friendly colour string (e.g. #FF0000) for this category.
    """


class LiveDataTimestampResultSchema(Schema):
    timestampUtc = fields.DateTime(format='iso', required=True, allow_none=True)

    @post_load
    def make_obj(self, js):
        return LiveDataTimestampResult(**js)


class LinkInfoSchema(Schema):
    linkId = fields.Integer(required=True)
    isFwd = fields.Boolean(required=True)
    angle = fields.Float(required=True)
    lengthMetres = fields.Float(required=True)
    speedKmph = fields.Float(required=True, allow_none=True)
    travelTimeMinutes = fields.Float(required=True, allow_none=True)
    quality = fields.Integer(required=True, allow_none=True)

    @post_load
    def make_obj(self, js):
        return LinkInfo(**js)


class LiveDataResultSchema(Schema):
    timestampUtc = fields.DateTime(format='iso', required=True, allow_none=True)
    data = fields.Nested(LinkInfoSchema, many=True, required=True)

    @post_load
    def make_obj(self, js):
        return LiveDataResult(**js)


class LiveDataAtPointResultSchema(Schema):
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    timestampUtc = fields.DateTime(format='iso', required=True, allow_none=True)
    data = fields.Nested(LinkInfoSchema, many=True, required=True)

    @post_load
    def make_obj(self, js):
        return LiveDataAtPointResult(**js)


class ColourLegendItemSchema(Schema):
    name = fields.String()
    colour = fields.String()

    @post_load
    def make_obj(self, js):
        return ColourLegendItem(**js)


class RTDS(TransLinkAPIBase):
    """
    The wrapper around TransLink's Regional Traffic Data System API.
    """

    def __init__(self, api_key, session=None):
        """
        :param api_key: TransLink API key.
        :param requests.Session session: Session to use, instead of the default.
        """
        super(RTDS, self).__init__(
            'https://rtdsapi.translink.ca/rtdsapi/v1/',
            api_key=api_key, session=session)

    def tile(self, destination, x, y, z, types=None):
        """
        Downloads a map tile for the provided position, showing roadways of the provided type.

        :param destination: Save the tile to this local file path.
        :param int x: The x-coordinate of the tile.
        :param int y: The y-coordinate of the tile.
        :param int z: The z-coordinate of the tile.
        :param int types:
            The types of roadway to display on the tile, as a bitwise-OR of highway (4),
            major roadway network (2) and arterial (1). For example, to show highway and
            arterial roadways, the value should be 5. If omitted, defaults to all roadway types.
        """
        return self._streamed_download(
            'Tile', destination,
            params={'x': x, 'y': y, 'z': z, 'types': types})

    def live_data_timestamp(self):
        """
        Returns the date and time at which the live data was last updated, in UTC.

        :rtype: LiveDataTimestampResult
        """
        return self._get_deserialized('LiveDataTimestampUtc', LiveDataTimestampResultSchema())

    def all_live_data(self):
        """
        Returns real-time data for all links.

        :rtype: LiveDataResult
        """
        return self._get_deserialized('AllLiveData', LiveDataResultSchema())

    def live_data_at_point(self, x, y, z=None, types=None):
        """
        Returns real-time data for links near the specified point.

        :param float x: The x-coordinate (longitude) of the point to look-up.
        :param float y: The y-coordinate (latitude) of the point to look-up.
        :param int z: The zoom level of the map on which the click occurred.
            Has an impact on the tolerance used when matching links.
            Defaults to a generous tolerance if not provided.
        :param int types: The types of roadway being displayed, should match displayed tile types.
            See ``types`` argument of :meth:`tile` for more details.
        :rtype: LiveDataAtPointResult
        """
        return self._get_deserialized(
            'LiveDataAtPoint', LiveDataAtPointResultSchema(),
            params={'x': x, 'y': y, 'z': z, 'types': types})

    def colour_legend(self):
        """
        Returns legend colour details.

        :rtype: list[ColourLegendItem]
        """
        return self._get_deserialized('ColourLegend', ColourLegendItemSchema(many=True))
