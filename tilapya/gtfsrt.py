"""
GTFS-realtime is a specification for sharing real-time transit information.
It's primarily ingested by Google in order to power transit information within Google Maps.

.. seealso:: `TransLink's GTFS-realtime API reference <https://developer.translink.ca/ServicesGtfs/ApiReference>`_.
    Much of it is replicated here for convenience.
    However, the docs here reflect Tilapya-specific behaviour.

Usage example
-------------

.. code-block:: python
   :caption: Request the real-time positions feed.

    >>> from tilapya import GTFSRT
    >>> api = GTFSRT('my key')
    >>> api.position()
    <Response [200]>

The protobuf data in ``response.content`` can then be deserialized.
"""
from ._util import TransLinkAPIBase
from .errors import TransLinkAPIError


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
            'https://gtfs.translink.ca/v2',
            api_key=api_key, session=session)

    def trip_updates(self):
        """
        Request the trip updates feed.

        :returns: The response. The raw protobuf data is in ``content``.
        :rtype: requests.Response
        """
        resp = self._request('gtfsrealtime')
        if not resp.ok:
            raise TransLinkAPIError(resp)
        return resp

    def position(self):
        """
        Request the position feed.

        :returns: The response. The raw protobuf data is in ``content``.
        :rtype: requests.Response
        """
        resp = self._request('gtfsposition')
        if not resp.ok:
            raise TransLinkAPIError(resp)
        return resp

    def service_alerts(self):
        """
        Request the service alerts feed.

        :returns: The response. The raw protobuf data is in ``content``.
        :rtype: requests.Response
        """
        resp = self._request('gtfsalerts')
        if not resp.ok:
            raise TransLinkAPIError(resp)
        return resp
