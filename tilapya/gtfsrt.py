"""
GTFS-realtime is a specification for sharing real-time transit information.
It's primarily ingested by Google in order to power transit information within Google Maps.

.. seealso:: `TransLink's GTFS-realtime API reference <https://developer.translink.ca/ServicesGtfs/ApiReference>`_.
    Much of it is replicated here for convenience.
    However, the docs here reflect Tilapya-specific behaviour.

Usage example
-------------

.. code-block:: python
   :caption: Download real-time positions to a file.

    >>> from tilapya import GTFSRT
    >>> api = GTFSRT('my key')
    >>> api.download_position('gtfsposition.pb')
    28791


"""
from collections import namedtuple

from marshmallow import Schema, fields, post_load

from ._util import TransLinkAPIBase
from .errors import TransLinkAPIError


class Headers(namedtuple('Headers', ['content_disposition', 'content_length', 'content_type', 'date', 'server'])):
    """
    HTTP headers for a GTFS-realtime feed file.

    :ivar content_disposition: Content-Disposition header.
    :ivar int content_length: Content-Length header.
    :ivar content_type: Content-Type header.
    :ivar datetime.datetime date: Parsed Date header.
    :ivar server: Server header.
    """


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
    The wrapper around TransLink's endpoints for GTFS-realtime datasets.
    """

    def __init__(self, api_key, session=None):
        """
        :param api_key: TransLink API key.
        :param requests.Session session: Session to use, instead of the default.
        """
        super(GTFSRT, self).__init__(
            'https://gtfs.translink.ca/',
            api_key=api_key, session=session)

    def _get_headers_and_deserialize(self, endpoint):
        with self._request(endpoint) as resp:
            if not resp.ok:
                raise TransLinkAPIError(resp)
            return HeadersSchema().load(resp.headers)

    def headers_realtime(self):
        """
        Get the headers for the trip updates feed.

        .. note:: This is implemented as a GET, as the server disallows HEAD.

        :rtype: Headers
        """
        return self._get_headers_and_deserialize('gtfsrealtime')

    def download_realtime(self, destination):
        """
        Download the trip updates feed.

        :param destination: Download the file to this local file path.
        :returns: Number of bytes downloaded.
        """
        return self._streamed_download('gtfsrealtime', destination)

    def headers_position(self):
        """
        Get the headers for the position feed.

        .. note:: This is implemented as a GET, as the server disallows HEAD.

        :rtype: Headers
        """
        return self._get_headers_and_deserialize('gtfsposition')

    def download_position(self, destination):
        """
        Download the position feed.

        :param destination: Download the file to this local file path.
        :returns: Number of bytes downloaded.
        """
        return self._streamed_download('gtfsposition', destination)
