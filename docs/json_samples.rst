JSON response samples
=====================

.. contents::
   :local:


RTTI
----

Stop
^^^^

Buses
^^^^^

``GET http://api.translink.ca/rttiapi/v1/buses``

::

    [
        {
            "VehicleNo": "11303",
            "TripId": 9287793,
            "RouteNo": "252",
            "Direction": "EAST",
            "Destination": "PARK ROYAL - ONLY",
            "Pattern": "EB1NEW",
            "Latitude": 49.331583,
            "Longitude": -123.15765,
            "RecordedTime": "05:20:01 pm",
            "RouteMap": {
                "Href": "http://nb.translink.ca/geodata/252.kmz"
            }
        },
        {
            "VehicleNo": "11304",
            "TripId": 9287801,
            "RouteNo": "252",
            "Direction": "WEST",
            "Destination": "INGLEWOOD",
            "Pattern": "WB1NEW",
            "Latitude": 49.331433,
            "Longitude": -123.147833,
            "RecordedTime": "05:20:29 pm",
            "RouteMap": {
                "Href": "http://nb.translink.ca/geodata/252.kmz"
            }
        },
    ]


``GET http://api.translink.ca/rttiapi/v1/buses/2543``

::

    {
        "VehicleNo": "2543",
        "TripId": 9263935,
        "RouteNo": "020",
        "Direction": "SOUTH",
        "Destination": "VICTORIA",
        "Pattern": "SB1",
        "Latitude": 49.280983,
        "Longitude": -123.116517,
        "RecordedTime": "10:05:13 pm",
        "RouteMap": {
            "Href": "http://nb.translink.ca/geodata/020.kmz"
        }
    }
