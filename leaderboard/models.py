from decimal import Decimal

from django.db import models

from catalog.models import Dish


class DishAggregateScore(models.Model):
    dish = models.OneToOneField(Dish, on_delete=models.CASCADE, related_name="aggregate_score")
    composite_score = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"))
    avg_overall_score = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("0.000"))
    rating_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-avg_overall_score", "-rating_count", "dish__name"]

    def __str__(self) -> str:
        return f"{self.dish.name}: {self.composite_score}"
