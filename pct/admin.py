from django.contrib import admin
from .models import HalfmileWaypoint, Post, Location


@admin.register(HalfmileWaypoint)
class HalfmileWaypointAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude"]
    list_filter = ["type"]
    ordering = ["name"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
