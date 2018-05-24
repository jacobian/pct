from django.contrib import admin
from .models import HalfmileWaypoint


@admin.register(HalfmileWaypoint)
class HalfmileWaypointAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude"]
    ordering = ["name"]
    search_fields = ["name"]
