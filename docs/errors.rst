Error handling
==============

If an error response is received from the TransLink Open API,
:class:`tilapya.TransLinkAPIError` is raised.
This class parses the error body and exposes its values as members.


.. autoclass:: tilapya.TransLinkAPIError
   :members:


If there was a problem deserializing the response according to the expected schema,
:class:`marshmallow.exceptions.ValidationError` is raised from
the `marshmallow <https://marshmallow.readthedocs.io>`_ library.
This should not occur unless the underlying API changes significantly.
