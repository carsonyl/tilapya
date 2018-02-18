import pytest
import os


@pytest.fixture
def valid_api_key():
    key = os.environ.get('TRANSLINK_API_KEY')
    if not key:
        raise KeyError('TRANSLINK_API_KEY environment variable must be set for tests.')
    return key


def sanitize_response(response):
    headers = response['headers']
    headers.pop('Set-Cookie', None)
    return response


@pytest.fixture
def vcr_config():
    return {
        'filter_headers': ['user-agent', 'set-cookie', 'connection'],
        'filter_query_parameters': ['apikey'],
        'decode_compressed_response': True,
        'before_record_response': sanitize_response,
    }
