from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point


class HalfmileWaypointManager(models.Manager):

    def closest_to(self, latitude, longitude, max_dist=D(mi=100)):
        p = Point(longitude, latitude)
        qs = self.filter(point__distance_lte=(p, max_dist))
        qs = qs.annotate(distance=Distance("point", p))
        qs = qs.order_by("distance")
        return qs[0]


class HalfmileWaypoint(models.Model):
    point = PointField()
    name = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    elevation = models.FloatField(blank=True, null=True)
    symbol = models.TextField(blank=True)

    objects = HalfmileWaypointManager()

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.point.y

    @property
    def longitude(self):
        return self.point.x
