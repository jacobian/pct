from django.contrib import admin
from .models import HalfmileWaypoint, Post, Location, Gallery, Photo, Breadcrumb


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


class PhotoInline(admin.StackedInline):
    model = Photo
    min_num = 1
    extra = 1


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]


@admin.register(Breadcrumb)
class BreadcrumbAdmin(admin.ModelAdmin):
    pass
