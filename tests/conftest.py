import pytest
import os


@pytest.fixture
def valid_api_key():
    key = os.environ.get('TRANSLINK_API_KEY')
    if not key:
        raise KeyError('TRANSLINK_API_KEY environment variable must be set for tests.')
    return key
