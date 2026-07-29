from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Dish, DishType
from ratings.models import RatingSubmission


class DishTypeListView(ListView):
    model = DishType
    template_name = "catalog/dish_type_list.html"
    context_object_name = "dish_types"

    def get_queryset(self):
        return (
            DishType.objects
            .filter(is_active=True)
            .annotate(dish_count=Count("dishes", filter=Q(dishes__is_published=True)))
        )


class DishByTypeView(ListView):
    template_name = "catalog/dish_by_type.html"
    context_object_name = "dishes"

    def get_dish_type(self):
        if not hasattr(self, "_dish_type"):
            self._dish_type = get_object_or_404(DishType, slug=self.kwargs["type_slug"], is_active=True)
        return self._dish_type

    def get_queryset(self):
        return (
            Dish.objects
            .select_related("dish_type", "venue")
            .filter(dish_type=self.get_dish_type(), is_published=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dish_type"] = self.get_dish_type()
        return context


class DishDetailView(DetailView):
    model = Dish
    template_name = "catalog/dish_detail.html"
    context_object_name = "dish"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Dish.objects.select_related("dish_type", "venue").filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_submissions"] = (
            RatingSubmission.objects
            .filter(dish=self.object)
            .select_related("user")
            .order_by("-created_at")
        )
        context["dish_type"] = self.object.dish_type
        return context
