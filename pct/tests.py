import datetime
import pytest
from . import models
from django.contrib.gis.geos import Point


def test_location_name():
    dt = datetime.datetime(2018, 1, 2, 3, 4, 5)
    p = Point(0, 0)
    mile_waypoint = models.HalfmileWaypoint(
        point=p, name="1", type=models.HalfmileWaypoint.MILE_TYPE
    )
    poi_waypoint = models.HalfmileWaypoint(
        point=p, name="FakePass", type=models.HalfmileWaypoint.POI_TYPE
    )

    l = models.Location(timestamp=dt)
    assert l.location_name == f"unknown location at {dt}"

    l.point = p
    assert l.location_name == str(p)

    l.closest_mile = mile_waypoint
    assert l.location_name == f"Mile {mile_waypoint.name}"

    l.closest_poi = poi_waypoint
    assert l.location_name == poi_waypoint.name

    l.location_override = "right here"
    assert l.location_name == "right here"
