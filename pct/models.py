from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class HalfmileWaypointManager(models.Manager):

    def closest_to(self, point, type=None):
        qs = self.filter(point__distance_lte=(point, D(mi=100)))
        if type:
            qs = qs.filter(type=type)
        qs = qs.annotate(distance=Distance("point", point))
        qs = qs.order_by("distance")
        try:
            return qs[0]
        except IndexError:
            return None


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
        if self.type == HalfmileWaypoint.MILE_TYPE:
            return "Mile " + self.name.replace("_", ".")
        else:
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
    location_override = models.TextField(blank=True, default="")

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
        if self.location_override:
            return self.location_override
        elif self.closest_poi:
            return str(self.closest_poi)
        elif self.closest_mile:
            return str(self.closest_mile)
        elif self.point:
            return str(self.point)
        else:
            return f"unknown location at {self.timestamp}"

    def __str__(self):
        return f"{self.__class__.__name__} at {self.location_name}"


class Post(Update):
    title = models.TextField(blank=True)
    text = MarkdownxField()

    @property
    def html(self):
        return mark_safe(markdownify(self.text))


class Location(Update):

    def __str__(self):
        return f"At {self.location_name}"


class InstagramPost(Update):
    instagram_id = models.CharField(unique=True, max_length=200)
    url = models.URLField(max_length=500)
    raw = JSONField()


class Breadcrumb(models.Model):
    """
    A raw track from the SPOT tracker

    Store this separate from the Location to prevent clutter, and to maybe use to display a live-ish track.
    """
    spot_id = models.BigIntegerField(unique=True)
    timestamp = models.DateTimeField()
    point = PointField()
    raw = JSONField()

    # For "OK" checkins, also save as a location.
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        related_name="breadcrumbs",
        on_delete=models.SET_NULL,
    )

    @property
    def latitude(self):
        return self.point.y

    @property
    def longitude(self):
        return self.point.x

    def __str__(self):
        return f"({self.latitude}, {self.longitude}) at {self.timestamp}"
