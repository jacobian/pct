from django.db.models import CharField, Value

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
