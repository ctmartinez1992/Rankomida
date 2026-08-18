import logging

from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from .forms import VenueSuggestionForm
from .models import Dish, DishType, SavedDish, Venue, VenueLocation, VenueSuggestion
from ratings.models import RatingSubmission

logger = logging.getLogger(__name__)


def _safe_redirect_url(request, fallback):
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    if next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return fallback


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
            .prefetch_related("venue__locations")
            .filter(is_published=True)
            .annotate(
                avg_score=Avg("rating_submissions__overall_score"),
                rating_count=Count("rating_submissions", distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dish_type"] = self.object.dish_type
        user = self.request.user
        if user.is_authenticated:
            context["user_has_rated"] = RatingSubmission.objects.filter(
                user=user, dish=self.object
            ).exists()
            context["is_saved"] = SavedDish.objects.filter(
                user=user, dish=self.object
            ).exists()
        else:
            context["user_has_rated"] = False
            context["is_saved"] = False
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
            .select_related("user", "venue_location", "venue_location__venue")
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
            .filter(is_published=True)
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
            Venue.objects
            .filter(is_published=True)
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )
        context["selected_city"] = self.request.GET.get("city", "")
        context["search_q"] = self.request.GET.get("q", "")
        context["sort"] = self.request.GET.get("sort", "")
        return context


class VenueDetailView(DetailView):
    model = Venue
    template_name = "catalog/venue_detail.html"
    context_object_name = "venue"

    def get_queryset(self):
        return Venue.objects.filter(is_published=True).prefetch_related("locations")

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


class VenueLocationDetailView(DetailView):
    model = VenueLocation
    template_name = "catalog/venue_location_detail.html"
    context_object_name = "location"

    def get_queryset(self):
        return (
            VenueLocation.objects
            .select_related("venue")
            .filter(
                venue__slug=self.kwargs["slug"],
                venue__is_published=True,
            )
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.venue.locations.count() < 2:
            return redirect("catalog:venue_detail", slug=self.object.venue.slug)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["venue"] = self.object.venue
        return context


class SavedDishListView(LoginRequiredMixin, ListView):
    template_name = "catalog/saved_list.html"
    context_object_name = "saved_dishes"

    def get_queryset(self):
        return (
            SavedDish.objects
            .filter(user=self.request.user, dish__is_published=True)
            .select_related("dish", "dish__dish_type", "dish__venue")
        )


@login_required
@require_POST
def save_dish(request, slug):
    dish = get_object_or_404(
        Dish.objects.select_related("dish_type").filter(is_published=True),
        slug=slug,
    )
    SavedDish.objects.get_or_create(user=request.user, dish=dish)
    fallback = reverse(
        "catalog:detail",
        kwargs={"type_slug": dish.dish_type.slug, "slug": dish.slug},
    )
    return redirect(_safe_redirect_url(request, fallback))


@login_required
@require_POST
def unsave_dish(request, slug):
    dish = get_object_or_404(Dish.objects.select_related("dish_type"), slug=slug)
    SavedDish.objects.filter(user=request.user, dish=dish).delete()
    fallback = reverse(
        "catalog:detail",
        kwargs={"type_slug": dish.dish_type.slug, "slug": dish.slug},
    )
    return redirect(_safe_redirect_url(request, fallback))


class VenueSuggestionCreateView(View):
    template_name = "catalog/suggest_venue.html"

    def get(self, request):
        q = request.GET.get("q", "").strip()
        authenticated = request.user.is_authenticated
        initial = {"name": q} if q else {}
        form = VenueSuggestionForm(initial=initial, authenticated=authenticated)
        return render(request, self.template_name, {
            "form": form,
            "search_q": q,
            "authenticated": authenticated,
        })

    def post(self, request):
        authenticated = request.user.is_authenticated
        form = VenueSuggestionForm(request.POST, authenticated=authenticated)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.search_query = request.GET.get("q", "").strip()
            if authenticated:
                suggestion.submitted_by = request.user
            suggestion.save()
            return redirect(reverse("catalog:suggest_venue_thanks"))
        q = request.GET.get("q", "").strip()
        return render(request, self.template_name, {
            "form": form,
            "search_q": q,
            "authenticated": authenticated,
        })
