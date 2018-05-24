import requests
import gpxpy
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from ...models import HalfmileWaypoint

SECTIONS = {"CA": "ABCDEFGHIJKLMNOPQR", "OR": "BCDEFG", "WA": "HIJLK"}


class Command(BaseCommand):
    help = "load halfmile waypoint data"

    def handle(self, *args, **options):
        for state, sections in SECTIONS.items():
            for section in sections:
                url = (
                    f"http://www.halfmilemedia.com/gpx/{state}_Sec_{section}_waypoints.gpx"
                )
                gpx = gpxpy.parse(requests.get(url).text)
                for waypoint in gpx.waypoints:
                    hw, created = HalfmileWaypoint.objects.update_or_create(
                        name=waypoint.name,
                        defaults=dict(
                            point=Point(waypoint.longitude, waypoint.latitude),
                            name=waypoint.name,
                            description=waypoint.description or "",
                            elevation=waypoint.elevation,
                            symbol=waypoint.symbol,
                            type=(
                                HalfmileWaypoint.MILE_TYPE
                                if waypoint.symbol == "Triangle, Red"
                                else HalfmileWaypoint.POI_TYPE
                            ),
                        ),
                    )
                print(f"Updated {state} section {section}")
