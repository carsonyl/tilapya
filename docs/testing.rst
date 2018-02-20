Testing
=======

Tilapya is thoroughly tested, with the goal of verifying both Tilapya and the Translink Open API.

Tests are written using `pytest <https://docs.pytest.org>`_, and are in the ``tests`` directory.

For performance and reproducibility, requests and responses for tests are
cached using `vcrpy <https://vcrpy.readthedocs.io>`_. This info is stored in ``tests/cassettes``.

Running the tests
-----------------

To run the tests, an API key for the TransLink Open API must be provided in
an environment variable named ``TRANSLINK_API_KEY``.

Ensure you have Tilapya's test dependencies:

::

    > pipenv install --dev

Then, to run the tests:

::

    > pipenv run py.test tests

The use of prerecorded responses can be configured using ``--vcr-record-mode``.
See `pytest-vcr <http://pytest-vcr.readthedocs.io/en/latest/configuration/#-vcr-record-mode>`_ docs for details.


Testing strategy
----------------

Generally, Tilapya's tests are written with two goals:

* Coverage of Tiliapya's own Python code
* Coverage of the TransLink Open API's documented and undocumented error states

HTTP status codes are usually ignored, as they have no consistent semantics.
