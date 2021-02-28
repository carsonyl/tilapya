"""
Tilapya's internal utilities. Not part of the public API.
"""
from requests import Session

from tilapya import __version__
from .errors import TransLinkAPIError


USER_AGENT = '{}/{}'.format("tilapya", __version__)


class TransLinkAPIBase(object):
    def __init__(self, base_url, api_key='', session=None):
        if not base_url.endswith('/'):
            base_url = base_url + '/'
        self._base_url = base_url

        self._api_key = api_key
        self._session = session or Session()
        self._ua = self._session.headers.get('User-Agent', '') + ' ' + USER_AGENT

    def _request(self, url_endpoint, method='GET', params=None, headers=None, **kwargs):
        params = params or {}
        params['apikey'] = self._api_key

        # Don't pass along parameters with null values.
        params = {k: v for k, v in params.items() if v is not None}

        headers = headers or {}
        headers['User-Agent'] = self._ua

        return self._session.request(
            method, self._base_url + url_endpoint,
            params=params, headers=headers, **kwargs)

    def _streamed_download(self, url_endpoint, destination, params=None):
        size = 0
        with self._request(url_endpoint, params=params, stream=True) as resp:
            if not resp.ok:
                raise TransLinkAPIError(resp)

            with open(destination, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)

        return size

    def _get_json(self, url_endpoint, params=None):
        return self._request(
            url_endpoint, method='GET', params=params,
            headers={'Accept': 'application/json'})

    def _get_deserialized(self, url_endpoint, schema, params=None):
        resp = self._get_json(url_endpoint, params=params)
        if not resp.ok:
            raise TransLinkAPIError(resp)

        return schema.loads(resp.text)
