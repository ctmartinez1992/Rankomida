from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from catalog.models import Dish, DishType


class CriteriaTemplate(models.Model):
    dish_type = models.ForeignKey(
        DishType,
        on_delete=models.CASCADE,
        related_name="criteria_templates",
    )
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.00"))
    min_score = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal("1.0"))
    max_score = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal("10.0"))
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["dish_type__name", "key"]
        unique_together = ("dish_type", "key")

    def __str__(self) -> str:
        return f"{self.dish_type.name}: {self.label}"


class RatingSubmission(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="rating_submissions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating_submissions",
    )
    overall_score = models.DecimalField(max_digits=4, decimal_places=1)
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "dish")

    def __str__(self) -> str:
        return f"{self.dish.name} by {self.user}"


class RatingCriterionScore(models.Model):
    submission = models.ForeignKey(
        RatingSubmission,
        on_delete=models.CASCADE,
        related_name="criterion_scores",
    )
    template = models.ForeignKey(
        CriteriaTemplate,
        on_delete=models.PROTECT,
        related_name="scores",
    )
    score = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        ordering = ["template__key"]
        unique_together = ("submission", "template")

    def clean(self):
        if self.template.dish_type_id != self.submission.dish.dish_type_id:
            raise ValidationError("Criterion template must match the submission dish type.")
        if self.score < self.template.min_score or self.score > self.template.max_score:
            raise ValidationError("Criterion score is outside the allowed range.")

    def __str__(self) -> str:
        return f"{self.template.key}: {self.score}"
