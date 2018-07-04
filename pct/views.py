import datetime
import json
import logging

import pytz
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.safestring import mark_safe

from .models import InstagramPost, Update, Post, DailyStats
from .combined_recent import combined_recent

log = logging.getLogger(__name__)


def index(request):
    type_qs_map = {}
    for model in Update.__subclasses__():
        model_name = model.__name__.lower()
        qs = model.objects.filter(show_on_timeline=True)
        qs = qs.select_related("closest_mile", "closest_poi")
        type_qs_map[model_name] = qs

    recent_updates = combined_recent(50, datetime_field="timestamp", **type_qs_map)

    # Add a "template" key for rendering a snippet template for each type
    for update in recent_updates:
        update["template"] = f'update_snippets/{update["type"]}.html'

    # Figure out my most recent location - that is, the first update with an assoicated point
    try:
        latest_location = next(u["object"] for u in recent_updates if u["object"].point)
        latest_location = [latest_location.latitude, latest_location.longitude]
    except StopIteration:
        latest_location = None

    # Construct a JSON blob to stick in the template, which will get read by
    # the JS code to build out the leaflet map. This is to avoid too much
    # mixing of template code with JS, which is gnarly.
    json_updates = []
    for update in recent_updates:
        location = (
            [update["object"].latitude, update["object"].longitude]
            if update["object"].point
            else None
        )
        json_updates.append({"location": location, "name": str(update["object"])})

    json_data = mark_safe(
        json.dumps({"updates": json_updates, "latest_location": latest_location})
    )

    return render(
        request,
        "index.html",
        {"updates": recent_updates, "stats": _latest_stats(), "json_data": json_data},
    )


def detail(request, slug):
    return render(
        request,
        "detail.html",
        {"post": get_object_or_404(Post, slug=slug), "stats": _latest_stats()},
    )


def _latest_stats():
    try:
        return DailyStats.objects.latest("date")
    except DailyStats.DoesNotExist:
        return None


@require_POST
@csrf_exempt
def instagram_hook(request):
    """
    Recieve a Zapier webhook about a new Instagram post

    The Zap is configured pretty simply: Instagram -> Webhook, passing (as JSON)
    the full body of the Instagram post (see data/sample-instagram-payload.json).
    The only small trick is that I created an X-Zapier-Secret header in
    Zapier with a shared secret that this view checks against the one in
    settings. This prevents someone who reads this code from spaming the
    real API.

    This is way easier than trying to interact iwth the Instagram API directly
    (and also doesn't require Facebook to approve my API use). I wish Instagram
    offered a personal API, but this is close enough I guess.
    """
    if request.META["HTTP_X_ZAPIER_SECRET"] != settings.ZAPIER_WEBOOK_SECRET:
        raise SuspiciousOperation("Zapier secret header didn't match")

    payload = json.load(request)

    location = payload.get("location", None)
    if location and "longitude" in location and "latitude" in location:
        point = Point(float(location["longitude"]), float(location["latitude"]))
    else:
        log.warn("No location info for instagram post id=%s", payload["id"])
        point = None

    try:
        embed_html = requests.get(
            f'https://api.instagram.com/oembed/?url={payload["link"]}'
        ).json()["html"]
    except KeyError:
        log.warn("Couldn't fetch embed html (no html key)")
        embed_html = ""

    post, created = InstagramPost.objects.update_or_create(
        instagram_id=payload["id"],
        defaults={
            "point": point,
            "url": payload["link"],
            "raw": payload,
            "timestamp": pytz.utc.localize(
                datetime.datetime.utcfromtimestamp(int(payload["created_time"]))
            ),
            "embed_html": embed_html,
        },
    )
    return HttpResponse(status=201)

