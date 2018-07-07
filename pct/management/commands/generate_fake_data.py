import pathlib
import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from ...models import (
    DailyStats,
    Breadcrumb,
    Update,
    Post,
    iNaturalistObservation,
    InstagramPost,
    HalfmileWaypoint,
)
import random


class Command(BaseCommand):
    help = "Generate some fake timeline data"

    def handle(self, *args, **options):
        confirm = input("Are you sure? Type 'yes' to continue: ")

        mile = 2650
        for day in range(50):
            wpt = HalfmileWaypoint.objects.get(type="mile", name=str(mile))
            date = settings.START_DATE + datetime.timedelta(days=day)
            Post.objects.create(timestamp=date, closest_mile=wpt)
            DailyStats.objects.update_or_create_for_date(date)
            mile -= random.randint(5, 25)
