from django.conf import settings as django_settings
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Dish, DishType, Venue
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
        return (
            Dish.objects
            .select_related("dish_type", "venue")
            .filter(is_published=True)
            .annotate(
                avg_score=Avg("rating_submissions__overall_score"),
                rating_count=Count("rating_submissions", distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dish_type"] = self.object.dish_type
        return context


_SORT_ORDERS = {
    "newest": "-created_at",
    "oldest": "created_at",
    "highest": "-overall_score",
    "lowest": "overall_score",
}


class CommunityNotesFragmentView(View):
    template_name = "catalog/_community_notes.html"

    def get(self, request, type_slug, slug):
        dish = get_object_or_404(
            Dish.objects.select_related("dish_type", "venue"),
            slug=slug,
            dish_type__slug=type_slug,
            is_published=True,
        )
        sort = request.GET.get("sort", "newest")
        if sort not in _SORT_ORDERS:
            sort = "newest"
        ordering = _SORT_ORDERS[sort]

        qs = (
            RatingSubmission.objects
            .filter(dish=dish)
            .select_related("user", "venue_location")
            .order_by(ordering)
        )

        page_size = getattr(django_settings, "COMMUNITY_NOTES_PAGE_SIZE", 10)
        paginator = Paginator(qs, page_size)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            "dish": dish,
            "page_obj": page_obj,
            "current_sort": sort,
            "sort_options": [
                ("Newest", "newest"),
                ("Oldest", "oldest"),
                ("Highest", "highest"),
                ("Lowest", "lowest"),
            ],
        })


class VenueListView(ListView):
    model = Venue
    template_name = "catalog/venue_list.html"
    context_object_name = "venues"

    def get_queryset(self):
        qs = (
            Venue.objects
            .annotate(dish_count=Count("dishes", filter=Q(dishes__is_published=True)))
        )
        city = self.request.GET.get("city", "").strip()
        if city:
            qs = qs.filter(city=city)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        if self.request.GET.get("sort") == "dishes":
            qs = qs.order_by("-dish_count")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = (
            Venue.objects.values_list("city", flat=True).distinct().order_by("city")
        )
        context["selected_city"] = self.request.GET.get("city", "")
        context["search_q"] = self.request.GET.get("q", "")
        context["sort"] = self.request.GET.get("sort", "")
        return context


class VenueDetailView(DetailView):
    model = Venue
    template_name = "catalog/venue_detail.html"
    context_object_name = "venue"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dishes"] = (
            Dish.objects
            .filter(venue=self.object, is_published=True)
            .select_related("dish_type")
            .annotate(
                avg_score=Avg("rating_submissions__overall_score"),
                rating_count=Count("rating_submissions", distinct=True),
            )
            .order_by("name")
        )
        return context
