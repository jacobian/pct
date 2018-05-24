from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.utils import timezone


class HalfmileWaypointManager(models.Manager):

    def closest_to(self, latitude, longitude, type=None):
        p = Point(longitude, latitude)
        qs = self.filter(point__distance_lte=(p, D(mi=100)))
        if type:
            qs = qs.filter(type=type)
        qs = qs.annotate(distance=Distance("point", p))
        qs = qs.order_by("distance")
        return qs[0]


class HalfmileWaypoint(models.Model):
    point = PointField()
    name = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    elevation = models.FloatField(blank=True, null=True)
    symbol = models.TextField(blank=True)

    MILE_TYPE = "mile"
    POI_TYPE = "poi"
    TYPE_CHOICES = ((MILE_TYPE, "mile"), (POI_TYPE, "point of interest"))
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    objects = HalfmileWaypointManager()

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.point.y

    @property
    def longitude(self):
        return self.point.x


class Update(models.Model):

    class Meta:
        abstract = True

    timestamp = models.DateTimeField(default=timezone.now)
    point = PointField(blank=True, null=True)

    def __str__(self):
        return f"{self.__class__.__name__} at {self.timestamp}"


class Post(Update):
    title = models.TextField(blank=True)
    text = models.TextField()


class Location(Update):
    pass


# class Photo(Update):
# class Gallery(Update): pass
