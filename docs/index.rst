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


License
-------

Copyright 2018 Carson Lam

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
