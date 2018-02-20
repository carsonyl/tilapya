JSON response samples
=====================

.. contents::
   :local:


RTDS
----

Live data at point
^^^^^^^^^^^^^^^^^^

``GET https://rtdsapi.translink.ca/rtdsapi/v1/LiveDataAtPoint?x=-123.045501&y=49.231947&types=6``

::

    {
        "x": -123.04546818137169,
        "y": 49.23298503849685,
        "timestampUtc": "2018-02-20T04:50:00",
        "data": [
            {
                "linkId": 32917581,
                "isFwd": true,
                "lengthMetres": 103.61,
                "angle": 270.8,
                "speedKmph": 31.7,
                "travelTimeMinutes": 0.2,
                "quality": 0
            },
            {
                "linkId": 32917581,
                "isFwd": false,
                "lengthMetres": 103.61,
                "angle": 90.8,
                "speedKmph": 37.8,
                "travelTimeMinutes": 0.2,
                "quality": 0
            }
        ]
    }


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
