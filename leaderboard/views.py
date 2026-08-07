import logging

from django.db.models import Avg, Count, Q
from django.views.generic import ListView

from catalog.models import Dish, DishType
from ratings.models import CriteriaTemplate

logger = logging.getLogger(__name__)


class LeaderboardListView(ListView):
    template_name = "leaderboard/leaderboard.html"
    context_object_name = "entries"

    def _get_criterion(self, dish_type):
        key = self.request.GET.get("criterion", "").strip()
        if not key or dish_type is None:
            return None
        criterion = CriteriaTemplate.objects.filter(
            dish_type=dish_type, key=key, is_active=True
        ).first()
        if criterion is None:
            logger.warning(
                "leaderboard.criterion_not_found dish_type=%s key=%s",
                dish_type.slug if dish_type else None,
                key,
            )
        else:
            logger.debug(
                "leaderboard.criterion_resolved dish_type=%s key=%s",
                dish_type.slug,
                key,
            )
        return criterion

    def get_queryset(self):
        slug = self.kwargs.get("dish_type_slug")
        dish_type = DishType.objects.filter(slug=slug, is_active=True).first() if slug else None

        criterion = self._get_criterion(dish_type)

        if criterion is not None:
            score_annotation = Avg(
                "rating_submissions__criterion_scores__score",
                filter=Q(rating_submissions__criterion_scores__template=criterion),
            )
        else:
            score_annotation = Avg("rating_submissions__overall_score")

        qs = (
            Dish.objects.filter(is_published=True, dish_type__is_active=True)
            .select_related("dish_type", "venue")
            .annotate(
                sort_score=score_annotation,
                rating_count=Count("rating_submissions", distinct=True),
            )
            .filter(sort_score__isnull=False)
            .order_by("-sort_score", "-rating_count", "name")
        )

        if dish_type is not None:
            qs = qs.filter(dish_type=dish_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dish_types"] = DishType.objects.filter(is_active=True)

        slug = self.kwargs.get("dish_type_slug")
        dish_type = DishType.objects.filter(slug=slug, is_active=True).first() if slug else None
        context["current_dish_type"] = dish_type

        if dish_type is not None:
            context["criteria_templates"] = CriteriaTemplate.objects.filter(
                dish_type=dish_type, is_active=True
            )
            context["current_criterion"] = self._get_criterion(dish_type)
        else:
            context["criteria_templates"] = []
            context["current_criterion"] = None

        return context
