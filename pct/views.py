import json
import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import SuspiciousOperation
from django.db.models import CharField, Value
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import InstagramPost, Update

log = logging.getLogger(__name__)


def index(request):
    type_qs_map = {
        model.__name__.lower(): model.objects.all() for model in Update.__subclasses__()
    }
    recent_updates = combined_recent(50, datetime_field="timestamp", **type_qs_map)
    for update in recent_updates:
        update["template"] = f'update_snippets/{update["type"]}.html'
    return render(request, "index.html", {"updates": recent_updates})


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

    try:
        point = Point(
            float(payload["location"]["longitude"]),
            float(payload["location"]["latitude"]),
        )
    except KeyError:
        log.warn("No location info for instagram post id=%s", payload["id"])
        point = None

    post = InstagramPost.objects.update_or_create(
        instagram_id=payload["id"],
        defaults={"point": point, "url": payload["link"], "raw": payload},
    )
    return HttpResponse(status=201)


# From https://simonwillison.net/2018/Mar/25/combined-recent-additions/
# Thanks, Simon!
def combined_recent(limit, **kwargs):
    datetime_field = kwargs.pop("datetime_field", "created")
    querysets = []
    for key, queryset in kwargs.items():
        querysets.append(
            queryset.annotate(
                recent_changes_type=Value(key, output_field=CharField())
            ).values("pk", "recent_changes_type", datetime_field)
        )
    union_qs = querysets[0].union(*querysets[1:])
    records = []
    for row in union_qs.order_by("-{}".format(datetime_field))[:limit]:
        records.append(
            {
                "type": row["recent_changes_type"],
                "when": row[datetime_field],
                "pk": row["pk"],
            }
        )
    # Now we bulk-load each object type in turn
    to_load = {}
    for record in records:
        to_load.setdefault(record["type"], []).append(record["pk"])
    fetched = {}
    for key, pks in to_load.items():
        for item in kwargs[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # Annotate 'records' with loaded objects
    for record in records:
        record["object"] = fetched[(record["type"], record["pk"])]
    return records
