from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import HalfmileWaypoint, Post, Location, InstagramPost, Breadcrumb


@admin.register(HalfmileWaypoint)
class HalfmileWaypointAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude"]
    list_filter = ["type"]
    ordering = ["name"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    pass


@admin.register(Breadcrumb)
class BreadcrumbAdmin(admin.ModelAdmin):
    pass
