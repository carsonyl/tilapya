from ._util import TransLinkAPIBase
from marshmallow import Schema, fields, post_load
from collections import namedtuple


LiveDataTimestampResult = namedtuple('LiveDataTimestampResult', ['timestampUtc'])
LiveDataResult = namedtuple('LiveDataResult', ['timestampUtc', 'data'])
LinkInfo = namedtuple('LinkInfo', ['linkId', 'isFwd', 'angle', 'lengthMetres', 'speedKmph', 'travelTimeMinutes', 'quality'])
LiveDataAtPointResult = namedtuple('LiveDataAtPointResult', ['x', 'y', 'timestampUtc', 'data'])
ColourLegendItem = namedtuple('ColourLegendItem', ['name', 'colour'])


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
    TransLink's Regional Traffic Data System API.
    """

    def __init__(self, api_key, session=None):
        super(RTDS, self).__init__(
            'https://rtdsapi.translink.ca/rtdsapi/v1/', 
            api_key=api_key, session=session)

    def tile(self, destination, x, y, z, types=None):
        return self._streamed_download('Tile', destination, 
            params={'x': x, 'y': y, 'z': z, 'types': types})
        
    def live_data_timestamp(self):
        return self._get_deserialized('LiveDataTimestampUtc', LiveDataTimestampResultSchema())

    def all_live_data(self):
        return self._get_deserialized('AllLiveData', LiveDataResultSchema())

    def live_data_at_point(self, x, y, z=None, types=None):
        return self._get_deserialized(
            'LiveDataAtPoint', LiveDataAtPointResultSchema(), 
            params={'x': x, 'y': y, 'z': z, 'types': types})

    def colour_legend(self):
        return self._get_deserialized('ColourLegend', ColourLegendItemSchema(many=True))
