import markdownx.urls
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from . import views
from .feeds import PostsFeed

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("instagram-hook/", views.instagram_hook),
    path("markdownx/", include(markdownx.urls)),
    path("feed/", PostsFeed(), name="feed"),
    path("<slug>/", views.detail, name="post-detail"),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))

