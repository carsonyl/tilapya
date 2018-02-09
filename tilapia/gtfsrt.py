from ._util import TransLinkAPIBase
from collections import namedtuple
from marshmallow import Schema, fields, post_load


Headers = namedtuple('Headers', ['content_disposition', 'content_length', 'content_type', 'date', 'server'])


class HeadersSchema(Schema):
    content_disposition = fields.String(load_from='Content-Disposition')
    content_length = fields.Integer(load_from='Content-Length')
    content_type = fields.String(load_from='Content-Type')
    date = fields.DateTime(format='rfc', load_from='Date')
    server = fields.String(load_from='Server')

    @post_load
    def make_obj(self, js):
        return Headers(**js)


class GTFSRT(TransLinkAPIBase):
    """
    TransLink's endpoints for GTFS-realtime datasets.
    """

    def __init__(self, api_key, session=None):
        super(GTFSRT, self).__init__(
            'https://gtfs.translink.ca/', 
            api_key=api_key, session=session)

    def _get_headers_and_deserialize(self, endpoint):
        with self._request(endpoint) as resp:
            if not resp.ok:
                resp.raise_for_status()
            return HeadersSchema().load(resp.headers)

    def headers_realtime(self):
        return self._get_headers_and_deserialize('gtfsrealtime')

    def download_realtime(self, destination):
        return self._streamed_download('gtfsrealtime', destination)

    def headers_position(self):
        return self._get_headers_and_deserialize('gtfsposition')

    def download_position(self, destination):
        return self._streamed_download('gtfsposition', destination)
