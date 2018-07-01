import pytest
import datetime
from pct.models import Location, HalfmileWaypoint
from django.contrib.gis.geos import Point


def test_location_name():
    dt = datetime.datetime(2018, 1, 2, 3, 4, 5)
    p = Point(0, 0)
    mile_waypoint = HalfmileWaypoint(
        point=p, name="1_5", type=HalfmileWaypoint.MILE_TYPE
    )
    poi_waypoint = HalfmileWaypoint(
        point=p, name="FakePass", type=HalfmileWaypoint.POI_TYPE
    )

    l = Location(timestamp=dt)
    assert l.location_name == f"unknown location"

    l.point = p
    assert l.location_name == str(p)

    l.closest_mile = mile_waypoint
    assert l.location_name == f"Mile 1.5"

    l.closest_poi = poi_waypoint
    assert l.location_name == poi_waypoint.name

    l.location_override = "right here"
    assert l.location_name == "right here"


@pytest.fixture
def waypoints(db):
    return {
        "harts": HalfmileWaypoint.objects.create(
            point=Point(-120.735481, 48.721127),
            name="HartsPass",
            type=HalfmileWaypoint.POI_TYPE,
        ),
        "mile_2630": HalfmileWaypoint.objects.create(
            point=Point(-120.735481, 48.792901),
            name="2630",
            type=HalfmileWaypoint.MILE_TYPE,
        ),
        "bridge_of_gods": HalfmileWaypoint.objects.create(
            point=Point(-121.897533, 45.661792),
            name="BridgeOfGods",
            type=HalfmileWaypoint.POI_TYPE,
        ),
        "mile_2000": HalfmileWaypoint.objects.create(
            point=Point(-119.571582, 38.205751),
            name="2000",
            type=HalfmileWaypoint.MILE_TYPE,
        ),
    }


def test_waypoints_closest_to(waypoints):
    wp = HalfmileWaypoint.objects.closest_to(Point(-120.730, 48.720))
    assert wp == waypoints["harts"]


def test_waypoints_closest_to_type(waypoints):
    wp = HalfmileWaypoint.objects.closest_to(
        Point(-120.730, 48.720), type=HalfmileWaypoint.MILE_TYPE
    )
    assert wp == waypoints["mile_2630"]


def test_waypoints_closest_to_far_away(waypoints):
    wp = HalfmileWaypoint.objects.closest_to(
        Point(-116.578046, 33.20829)  # mile 100, very far away
    )
    assert wp == None


def test_update_save_updates_waypoint_from_point(waypoints):
    """if an update has a point but not waypoints, save() should update waypoints based on the closest to that point"""
    l = Location.objects.create(point=Point(-120.730, 48.720))
    assert l.closest_mile == waypoints["mile_2630"]
    assert l.closest_poi == waypoints["harts"]


def test_update_save_updates_point_from_waypoint(waypoints):
    """if an update has a waypoint but not a point, save() should update the point based on the waypoint"""
    l = Location.objects.create(closest_poi=waypoints["harts"])
    assert l.point == waypoints["harts"].point


def test_update_doesnt_stomp_existing_points(waypoints):
    """if an update has an existing point, don't stomp on it when saving"""
    p = Point(-120.730, 48.720)
    l = Location.objects.create(point=p, closest_poi=waypoints["harts"])
    assert l.point == p


def test_update_fills_in_mile_from_poi_and_vice_versa(waypoints):
    l = Location.objects.create(closest_poi=waypoints["harts"])
    assert l.closest_mile == waypoints["mile_2630"]

    l = Location.objects.create(closest_mile=waypoints["mile_2630"])
    assert l.closest_poi == waypoints["harts"]

