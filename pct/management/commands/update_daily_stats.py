from django.utils import timezone
from django.core.management.base import BaseCommand
from ...models import DailyStats


class Command(BaseCommand):
    help = "update daily stats for today"

    def handle(self, *args, **options):
        today = timezone.localdate()
        try:
            DailyStats.objects.update_or_create_for_date(today)
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated daily stats for {today}"))
