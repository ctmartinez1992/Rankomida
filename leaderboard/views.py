from django.views.generic import ListView

from catalog.models import DishType

from .models import DishAggregateScore


class LeaderboardListView(ListView):
    template_name = "leaderboard/leaderboard.html"
    context_object_name = "entries"

    def get_queryset(self):
        qs = (
            DishAggregateScore.objects.select_related("dish", "dish__venue", "dish__dish_type")
            .filter(dish__is_published=True, dish__dish_type__is_active=True)
            .order_by("-avg_overall_score", "-rating_count", "dish__name")
        )
        slug = self.kwargs.get("dish_type_slug")
        if slug:
            qs = qs.filter(dish__dish_type__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dish_types"] = DishType.objects.filter(is_active=True)
        slug = self.kwargs.get("dish_type_slug")
        context["current_dish_type"] = (
            DishType.objects.filter(slug=slug).first() if slug else None
        )
        return context
