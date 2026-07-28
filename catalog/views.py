from django.views.generic import DetailView, ListView

from .models import Dish
from ratings.models import RatingSubmission


class DishListView(ListView):
    model = Dish
    template_name = "catalog/dish_list.html"
    context_object_name = "dishes"

    def get_queryset(self):
        return (
            Dish.objects.select_related("dish_type", "venue")
            .filter(is_published=True, dish_type__is_active=True)
        )


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
        return context
