import requests
import dateutil.parser
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.gis.geos import Point
from ...models import Breadcrumb, Post

# SPOT message types to pay attention to
BREADCRUMB_MESSAGE_TYPES = ("OK", "TRACK", "UNLIMITED-TRACK", "EXTREME-TRACK")


class Command(BaseCommand):
    help = "load latest breadcrumb data from spot"

    def handle(self, *args, **options):
        # The SPOT API returns 50 items per page, so we have to paginate back to make sure we got everything.
        # If this were smarter (possible future improvement), we'd stop paginating once we're into messages
        # we've already seen. But, that's a bit trickier and I don't want to figure it out yet.

        # Fetch the first page (first 50 messages)
        response = self._fetch_feed()
        self._handle_feed(response)

        # That response tells how many messages there are total. Turn that into a list
        # of pages to fetch. We already got the first page (start=1), so don't re-fetch
        # that one.
        pages = range(51, response["totalCount"], 50)
        for page in pages:
            response = self._fetch_feed(page)
            self._handle_feed(response)

    def _fetch_feed(self, start=None):
        url = (
            f"https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/{settings.SPOT_FEED_ID}/message.json"
        )
        if start:
            url += f"?start={start}"
        response = requests.get(url).json()["response"]
        if "errors" in response:
            message = "SPOT API ERROR: [{code}] {text}: {description}".format(
                **response["errors"]["error"]
            )
            raise CommandError(message)
        return response["feedMessageResponse"]

    def _handle_feed(self, data):
        for message in data["messages"]["message"]:
            # Create or breadcrumbs for location track messages
            if message["messageType"] in BREADCRUMB_MESSAGE_TYPES:
                crumb, created = Breadcrumb.objects.update_or_create(
                    spot_id=message["id"],
                    defaults={
                        "point": Point(message["longitude"], message["latitude"]),
                        "timestamp": dateutil.parser.parse(message["dateTime"]),
                        "raw": message,
                    },
                )

                # For new "OK" messages, create a Post update also
                if created and message["messageType"] == "OK":
                    crumb.post = Post.objects.create(
                        point=crumb.point, timestamp=crumb.timestamp
                    )
                    crumb.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(crumb))

