import datetime
import requests
from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import text, timezone
from django.utils.safestring import mark_safe
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

# Where is Canda in trail miles?
# This could be determined from the data but w/e this is easy.
CANADA_MILE = 2652.6


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
            return "Mile " + self.name.replace("-", ".")
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
        ordering = ["-timestamp"]

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
        # Attempt to fill in missing location info based on what's there.
        # If there's a point but no waypoints, try to fill in waypoints based on proximity.
        # If there's a waypoint but no point, copy the waypoint's location to this.
        # The order's sneaky: do the waypoint -> point bit first, because that way a
        # waypoint of one type (POI or mile) will make there be a point, which'll then
        # fill in the waypoint of the other type.
        if not self.point:
            if self.closest_mile:
                self.point = self.closest_mile.point
            elif self.closest_poi:
                self.point = self.closest_poi.point

        if self.point and not self.closest_mile:
            self.closest_mile = HalfmileWaypoint.objects.closest_to(
                self.point, type=HalfmileWaypoint.MILE_TYPE
            )

        if self.point and not self.closest_poi:
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
            return f"unknown location"

    def __str__(self):
        return f"{self.__class__.__name__} at {self.location_name}"


class Post(Update):
    title = models.TextField(blank=True)
    slug = models.SlugField(
        blank=True,
        help_text="if this is blank, no individal url for the post will be available",
    )
    text = MarkdownxField()

    @property
    def html(self):
        return mark_safe(markdownify(self.text))

    def __str__(self):
        if self.title:
            return self.title
        else:
            return text.Truncator(self.text).words(10)


class Location(Update):

    def __str__(self):
        return f"At {self.location_name}"


class InstagramPost(Update):
    instagram_id = models.CharField(unique=True, max_length=200)
    embed_html = models.TextField(blank=True)
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


class DailyStatsManager(models.Manager):

    def update_or_create_for_date(self, date):
        if date > timezone.now().date():
            raise ValueError("Can't create stats for days in the future")

        # First look for a Location saved on that day.
        # That's likely to be SPOT OK message from camp, or a manual entry,
        # and will be the most accurate.
        try:
            locs = Location.objects.filter(timestamp__date=date).order_by("-timestamp")
            mile = locs[0].closest_mile
        except IndexError:
            # If that doesn't exist, look for the latest breadcrumb for the given day
            # the location is the closest mile to that breadcrumb
            try:
                crumbs = Breadcrumb.objects.filter(timestamp__date=date)
                latest_crumb = crumbs.order_by("-timestamp")[0]
                mile = HalfmileWaypoint.objects.closest_to(
                    crumb.point, type=HalfmileWaypoint.MILE_TYPE
                )
            except IndexError:
                mile = None

        if mile is None:
            raise ValueError(f"Can't create stats for {date} - no data")

        return self.update_or_create(
            date=date,
            defaults={"miles_hiked": CANADA_MILE - float(mile.name.replace("-", "."))},
        )


class DailyStats(models.Model):
    """
    Stats for a given day.

    Calculated automatically by a task, see above and the update_daily_stats tasks.

    All the math assumes a SOBO hike.

    Possible future: I could add other stats (like, zeros, did I shower, etc) here???
    """
    date = models.DateField()
    miles_hiked = models.FloatField()

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "daily stats"

    objects = DailyStatsManager()

    @property
    def miles_remaining(self):
        return CANADA_MILE - self.miles_hiked

    @property
    def days_elapsed(self):
        return (self.date - settings.START_DATE).days

    @property
    def miles_per_day(self):
        return self.miles_hiked / self.days_elapsed

    @property
    def projected_finish_date(self):
        projected_days_remaining = self.miles_remaining / self.miles_per_day
        return settings.START_DATE + datetime.timedelta(days=projected_days_remaining)
