from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.fields import JSONField
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
    closest_mile = models.ForeignKey(
        HalfmileWaypoint,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    closest_poi = models.ForeignKey(
        HalfmileWaypoint,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def save(self, *args, **kwargs):
        if self.point:
            self.closest_mile = HalfmileWaypoint.objects.closest_to(
                self.point, type=HalfmileWaypoint.MILE_TYPE
            )
            self.closest_poi = HalfmileWaypoint.objects.closest_to(
                self.point, type=HalfmileWaypoint.POI_TYPE
            )
        super().save(*args, **kwargs)

    @property
    def location_name(self):
        if self.closest_poi:
            loc = self.closest_poi.name
        elif self.closest_mile:
            loc = self.closest_mile.name
        elif self.point:
            loc = str(self.point)
        else:
            loc = str(self.timestamp)

    def __str__(self):
        return f"{self.__class__.__name__} at {self.location_name}"


class Post(Update):
    title = models.TextField(blank=True)
    text = models.TextField()


class Location(Update):

    def __str__(self):
        return f"At {self.location_name}"


class Gallery(Update):
    title = models.TextField(blank=True)
    text = models.TextField(blank=True)


class Photo(models.Model):
    photo = models.ImageField(upload_to="photos")
    gallery = models.ForeignKey(
        Gallery, related_name="photos", on_delete=models.CASCADE
    )


class Breadcrumb(models.Model):
    """
    A raw track from the SPOT tracker

    Store this separate from the Location to prevent clutter, and to maybe use to display a live-ish track.
    """
    spot_id = models.BigIntegerField(unique=True)
    timestamp = models.DateTimeField()
    point = PointField()
    raw = JSONField()

    # FIXME: maybe add closest mile/POI?

    @property
    def latitude(self):
        return self.point.y

    @property
    def longitude(self):
        return self.point.x

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) at {self.timestamp}"
