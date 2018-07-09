import datetime

import pytest
import pytz
from django.contrib.gis.geos import Point
from pct.models import DailyStats, HalfmileWaypoint, Post, InstagramPost, Update


def test_location_name():
    dt = datetime.datetime(2018, 1, 2, 3, 4, 5)
    p = Point(0, 0)
    mile_waypoint = HalfmileWaypoint(
        point=p, name="1-5", type=HalfmileWaypoint.MILE_TYPE
    )
    poi_waypoint = HalfmileWaypoint(
        point=p, name="FakePass", type=HalfmileWaypoint.POI_TYPE
    )

    post = Post(timestamp=dt)
    assert post.location_name == f"unknown location"

    post.point = p
    assert post.location_name == str(p)

    post.closest_mile = mile_waypoint
    assert post.location_name == f"Mile 1.5"

    # Camel case --> spacest

    post.closest_poi = poi_waypoint
    assert post.location_name == "Fake Pass"

    post.location_override = "right here"
    assert post.location_name == "right here"


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
        "mile_2146": HalfmileWaypoint.objects.create(
            point=Point(-121.888976, 45.658324),
            name="2146",
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
    assert wp == None  # noqa:E711


def test_update_save_updates_waypoint_from_point(waypoints):
    """if an update has a point but not waypoints, save() should update waypoints based on the closest to that point"""
    post = Post.objects.create(point=Point(-120.730, 48.720))
    assert post.closest_mile == waypoints["mile_2630"]
    assert post.closest_poi == waypoints["harts"]


def test_update_save_updates_point_from_waypoint(waypoints):
    """if an update has a waypoint but not a point, save() should update the point based on the waypoint"""
    post = Post.objects.create(closest_poi=waypoints["harts"])
    assert post.point == waypoints["harts"].point


def test_update_doesnt_stomp_existing_points(waypoints):
    """if an update has an existing point, don't stomp on it when saving"""
    p = Point(-120.730, 48.720)
    post = Post.objects.create(point=p, closest_poi=waypoints["harts"])
    assert post.point == p


def test_update_fills_in_mile_from_poi_and_vice_versa(waypoints):
    post = Post.objects.create(closest_poi=waypoints["harts"])
    assert post.closest_mile == waypoints["mile_2630"]

    post = Post.objects.create(closest_mile=waypoints["mile_2630"])
    assert post.closest_poi == waypoints["harts"]


@pytest.mark.django_db
def test_update_save_works_without_any_location():
    p = Post.objects.create(text="Content without a location")
    assert p.location_name == "unknown location"


def test_daily_stats_from_location(waypoints):
    ts = pytz.utc.localize(datetime.datetime(2018, 1, 2, 3, 4))
    Post.objects.create(timestamp=ts, closest_poi=waypoints["bridge_of_gods"])
    s, created = DailyStats.objects.update_or_create_for_date(ts.date())
    assert s.miles_hiked == pytest.approx(506.6)


@pytest.mark.django_db
def test_recent_updates():
    ts = pytz.utc.localize(datetime.datetime(2018, 1, 2, 3, 4))

    Post.objects.create(timestamp=ts, location_override="t1")

    ts += datetime.timedelta(minutes=10)
    InstagramPost.objects.create(
        timestamp=ts,
        instagram_id="xxx",
        url="https://example.com/",
        location_override="t2",
        raw={},
    )

    ts += datetime.timedelta(minutes=10)
    Post.objects.create(timestamp=ts, location_override="t3")

    recent_updates = Update.recent_updates()
    names = [update["object"].location_name for update in recent_updates]
    assert names == ["t3", "t2", "t1"]


def test_absolute_url_no_slug():
    p = Post(id=1)
    assert p.get_absolute_url() == "/#instagrampost-3"


def test_absolute_url_slug():
    p = Post(id=1, slug="foo")
    assert p.get_absolute_url() == "/foo/"
