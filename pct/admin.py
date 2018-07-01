from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import HalfmileWaypoint, Post, Location, InstagramPost, Breadcrumb
from django import forms

_base_update_fields = [
    "timestamp",
    "point",
    "closest_mile",
    "closest_poi",
    "location_override",
]
_base_update_autocomplete_fields = ["closest_mile", "closest_poi"]
_base_update_list_display = ["timestamp", "location_name"]


@admin.register(HalfmileWaypoint)
class HalfmileWaypointAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude"]
    list_filter = ["type"]
    ordering = ["name"]
    search_fields = ["name"]


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


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fields = _base_update_fields
    autocomplete_fields = _base_update_autocomplete_fields
    list_display = _base_update_list_display


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    fields = _base_update_fields + ["instagram_id", "url", "embed_html", "raw"]
    readonly_fields = ["instagram_id", "url", "embed_html", "raw"]
    autocomplete_fields = _base_update_autocomplete_fields
    list_display = ["url"] + _base_update_list_display


@admin.register(Breadcrumb)
class BreadcrumbAdmin(admin.ModelAdmin):
    list_display = ["point_display", "timestamp"]
    readonly_fields = ["spot_id", "raw"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"

    def point_display(self, breadcrumb):
        return f"({breadcrumb.latitude}, {breadcrumb.longitude})"
