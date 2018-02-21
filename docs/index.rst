Tilapya: TransLink API, in Python
=================================

.. image:: https://img.shields.io/pypi/v/tilapya.svg?maxAge=2592000
    :target: https://pypi.org/project/tilapya
.. image:: https://img.shields.io/travis/carsonyl/tilapya.svg?maxAge=2592000
    :target: https://travis-ci.org/carsonyl/tilapya
.. image:: https://readthedocs.org/projects/tilapya/badge/?version=latest
    :target: http://tilapya.readthedocs.io/en/latest/?badge=latest

**Tilapya** is a Python wrapper around the `TransLink Open API <https://developer.translink.ca/>`_,
which provides real-time transit information for the Metro Vancouver region.

Tilapya has three interfaces which correspond directly to components of the TransLink Open API:

* :doc:`RTTI <rtti>`: Real-Time Transit Information
* :doc:`RTDS <rtds>`: Regional Traffic Data System
* :doc:`GTFSRT <gtfsrt>`: GTFS-realtime feeds

Tilapya is more than a thin wrapper around the underlying REST APIs.
Where possible, it smooths over some inconvenient return values,
and guarantees a consistent schema in returned errors and responses.

Tilapya is licensed under Apache 2.0.


Installation
------------

Install Tilapya using `pip <https://pip.pypa.io>`_::

    $ pip install tilapya

The source is also `available on GitHub <https://github.com/carsonyl/tilapya>`_.


Getting started
---------------

Use of the TransLink Open API, and thus Tilapya, requires an API key.
If you don't already have an API key, you can get one by registering for an account at
https://developer.translink.ca/Account/Register.

Tilapya's documentation is at http://tilapya.readthedocs.io.
Tilapya's API docs contain examples for common operations.


Documentation
-------------

.. toctree::
   :maxdepth: 1

   rtti
   rtds
   gtfsrt
   errors
   testing
   history


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
