from django.contrib.syndication.views import Feed
from django import template

from .models import Update


class PostsFeed(Feed):
    title = "JKM on the PCT"
    link = "/"
    description = "Updates from Jacob's PCT hike"

    def items(self):
        return Update.recent_updates(20)

    def item_title(self, item):
        return str(item["object"])

    def item_link(self, item):
        return item["object"].get_absolute_url()

    def item_description(self, item):
        e = template.Engine.get_default()
        t = e.get_template(f'feed_descriptions/{item["type"]}.html')
        c = template.Context({"item": item})
        return t.render(c)
