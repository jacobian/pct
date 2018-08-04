from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import (
    HalfmileWaypoint,
    Post,
    InstagramPost,
    iNaturalistObservation,
    Breadcrumb,
    DailyStats,
)
from django import forms
from django.contrib.gis.db.models import PointField
from django.shortcuts import redirect

_base_update_fields = [
    "timestamp",
    "point",
    "closest_mile",
    "closest_poi",
    "location_override",
    "show_on_timeline",
    "deleted",
]
_base_update_autocomplete_fields = ["closest_mile", "closest_poi"]
_base_update_list_display = ["timestamp", "location_name", "deleted"]


@admin.register(HalfmileWaypoint)
class HalfmileWaypointAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "latitude", "longitude", "elevation", "description"]
    list_filter = ["type"]
    ordering = ["name"]
    search_fields = ["name"]
    readonly_fields = ["name", "description", "type", "elevation", "symbol", "point"]


class PostForm(forms.ModelForm):

    class Meta:
        fields = "__all__"
        model = Post
        widgets = {"title": forms.TextInput(), "location_override": forms.TextInput()}


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    form = PostForm
    fields = ["title", "slug", "text"] + _base_update_fields
    autocomplete_fields = _base_update_autocomplete_fields
    list_display = ["__str__"] + _base_update_list_display
    save_on_top = True
    formfield_overrides = {PointField: {"widget": forms.TextInput()}}


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    fields = _base_update_fields + ["instagram_id", "url", "embed_html", "raw"]
    readonly_fields = ["instagram_id", "url", "embed_html", "raw"]
    autocomplete_fields = _base_update_autocomplete_fields
    list_display = ["url"] + _base_update_list_display
    formfield_overrides = {PointField: {"widget": forms.TextInput()}}


@admin.register(iNaturalistObservation)
class iNaturalistObservationAdmin(admin.ModelAdmin):
    fields = _base_update_fields + [
        "inaturalist_id",
        "name",
        "url",
        "thumbnail_url",
        "raw",
    ]
    readonly_fields = ["inaturalist_id", "name", "url", "thumbnail_url", "raw"]
    autocomplete_fields = _base_update_autocomplete_fields
    list_display = ["name"] + _base_update_list_display
    formfield_overrides = {PointField: {"widget": forms.TextInput()}}


@admin.register(Breadcrumb)
class BreadcrumbAdmin(admin.ModelAdmin):
    list_display = ["point_display", "timestamp"]
    readonly_fields = ["spot_id", "raw", "point", "timestamp"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"
    formfield_overrides = {PointField: {"widget": forms.TextInput()}}

    def point_display(self, breadcrumb):
        return f"({breadcrumb.latitude}, {breadcrumb.longitude})"


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "miles_hiked",
        "miles_remaining",
        "days_elapsed",
        "miles_per_day",
        "projected_finish_date",
    ]

