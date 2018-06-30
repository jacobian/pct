from django.contrib import admin
from django.urls import path
from django.shortcuts import render

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda req: render(req, "index.html")),
    path("inner/", lambda req: render(req, "secondary.html")),
]
