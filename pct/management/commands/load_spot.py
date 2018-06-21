import requests
import dateutil.parser
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.gis.geos import Point
from ...models import Breadcrumb, Location

# SPOT message types to pay attention to
BREADCRUMB_MESSAGE_TYPES = ("OK", "TRACK", "UNLIMITED-TRACK", "EXTREME-TRACK")


class Command(BaseCommand):
    help = "load latest breadcrumb data from spot"

    def handle(self, *args, **options):
        # two options:
        #   A. load messages.json, parse, if we haven't hit a breadcrumb we've seen, go back a page (start=51, etc)
        #   B. load messages using startDate=date-of-last-message
        # What I'm not sure of and need to test: does B work if > 50 or do we need start also?
        #
        # Just to get this working as a POC, going to ignore that and just load the last 50 points regaurdless
        # Actually, that means there _is_ a
        #   C. naievely load last 50 points, and just ensure this runs often enough to get them all!

        url = (
            f"https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{settings.SPOT_FEED_ID}/message.json"
        )
        response = requests.get(url).json()["response"]
        if "errors" in response:
            message = "SPOT API ERROR: [{code}] {text}: {description}".format(
                **response["error"]
            )
            raise CommandError(message)

        for message in response["feedMessageResponse"]["messages"]["message"]:
            # Load messages
            if message["messageType"] in BREADCRUMB_MESSAGE_TYPES:
                crumb, created = Breadcrumb.objects.update_or_create(
                    spot_id=message["id"],
                    defaults={
                        "point": Point(message["longitude"], message["latitude"]),
                        "timestamp": dateutil.parser.parse(message["dateTime"]),
                        "raw": message,
                    },
                )

                # For new "OK" messages, create a Location update also
                if created and message["messageType"] == "OK":
                    crumb.location = Location.objects.create(
                        point=crumb.point, timestamp=crumb.timestamp
                    )
                    crumb.save()

                if created:
                    print(self.style.SUCCESS(crumb), end="", file=self.stdout)

