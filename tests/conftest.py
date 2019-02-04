import pytest
import os


@pytest.fixture
def valid_api_key():
    key = os.environ.get('TRANSLINK_API_KEY')
    if not key:
        raise KeyError('TRANSLINK_API_KEY environment variable must be set for tests.')
    return key


def remove_response_headers_func(*headers_to_remove):
    def sanitize_response(response):
        headers = response['headers']
        for header in headers_to_remove:
            headers.pop(header, None)
        return response
    return sanitize_response


@pytest.fixture(scope='module')
def vcr_config():
    return {
        'filter_headers': ['user-agent', 'set-cookie', 'connection'],
        'filter_query_parameters': ['apikey'],
        'decode_compressed_response': True,
        'before_record_response': remove_response_headers_func('Set-Cookie', 'Date'),
    }


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    return os.path.join('tests', 'cassettes', request.module.__name__)
