from django.core.management.base import BaseCommand

from leaderboard.services import recompute_all_aggregates


class Command(BaseCommand):
    help = "Recompute leaderboard aggregate snapshots for all published dishes."

    def handle(self, *args, **options):
        total = recompute_all_aggregates()
        self.stdout.write(
            self.style.SUCCESS(f"Recomputed leaderboard aggregates for {total} dishes.")
        )
