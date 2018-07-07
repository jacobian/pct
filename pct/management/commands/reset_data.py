import pathlib
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from ...models import (
    DailyStats,
    Breadcrumb,
    Update,
    Post,
    iNaturalistObservation,
    InstagramPost,
)

POSTS_DIR = pathlib.Path(__file__).parents[3] / "posts"


class Command(BaseCommand):
    help = "Reset timeline data"

    def handle(self, *args, **options):
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm == "yes":
            DailyStats.objects.all().delete()
            Breadcrumb.objects.all().delete()
            Post.objects.all().delete()

            # for iNat and Insta, just mark deleted (so I can save/undelete)
            iNaturalistObservation.objects.all().update(deleted=True)
            InstagramPost.objects.all().update(deleted=True)

            for postfile in POSTS_DIR.iterdir():
                Post.objects.update_or_create(
                    slug=postfile.stem,
                    defaults=dict(
                        title=postfile.stem.title(),
                        slug=postfile.stem,
                        text=postfile.read_text(),
                        show_on_timeline=False,
                    ),
                )
