from decimal import Decimal

from django.conf import settings

from catalog.models import Dish
from ratings.models import RatingSubmission

from .models import DishAggregateScore


def _submission_composite_score(submission: RatingSubmission) -> Decimal:
    weighted_total = Decimal("0")
    total_weight = Decimal("0")
    for criterion in submission.criterion_scores.select_related("template"):
        weighted_total += criterion.score * criterion.template.weight
        total_weight += criterion.template.weight

    overall_weight = Decimal(str(getattr(settings, "RANKING_OVERALL_WEIGHT", 1.0)))
    weighted_total += submission.overall_score * overall_weight
    total_weight += overall_weight

    if total_weight == 0:
        return Decimal("0")
    return weighted_total / total_weight


def recompute_dish_aggregate(dish: Dish) -> DishAggregateScore:
    submissions = (
        RatingSubmission.objects.filter(dish=dish)
        .prefetch_related("criterion_scores__template")
        .order_by("id")
    )

    count = submissions.count()
    if count == 0:
        composite = Decimal("0")
        avg_overall = Decimal("0")
    else:
        composite_sum = sum((_submission_composite_score(s) for s in submissions), Decimal("0"))
        composite = composite_sum / Decimal(count)
        overall_sum = sum((s.overall_score for s in submissions), Decimal("0"))
        avg_overall = overall_sum / Decimal(count)

    aggregate, _ = DishAggregateScore.objects.update_or_create(
        dish=dish,
        defaults={
            "composite_score": composite,
            "avg_overall_score": avg_overall,
            "rating_count": count,
        },
    )
    return aggregate


def recompute_all_aggregates() -> int:
    dishes = Dish.objects.filter(is_published=True).order_by("id")
    total = 0
    for dish in dishes:
        recompute_dish_aggregate(dish)
        total += 1
    return total
