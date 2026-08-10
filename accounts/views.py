import logging

from django.conf import settings as django_settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import ProfileVisibilityForm, RegistrationForm
from .models import UserProfile
from catalog.models import DishType
from ratings.models import RatingSubmission

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("accounts.registered user_id=%s", user.id)
            return redirect("catalog:list")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    userprofile, _ = UserProfile.objects.get_or_create(
        user=profile_user, defaults={"is_public": True}
    )
    if not userprofile.is_public and request.user != profile_user:
        logger.debug(
            "accounts.profile_private_blocked viewer=%s target=%s",
            request.user,
            profile_user.username,
        )
        return render(request, "accounts/profile_private.html", {"profile_user": profile_user})

    rating_count = RatingSubmission.objects.filter(user=profile_user).count()
    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "userprofile": userprofile,
        "rating_count": rating_count,
    })


_SORT_ORDERS = {
    "newest": "-created_at",
    "oldest": "created_at",
    "highest": "-overall_score",
    "lowest": "overall_score",
}


class ProfileRatingsFragmentView(View):
    template_name = "accounts/_profile_ratings.html"

    def get(self, request, username):
        profile_user = get_object_or_404(User, username=username)
        userprofile, _ = UserProfile.objects.get_or_create(
            user=profile_user, defaults={"is_public": True}
        )
        if not userprofile.is_public and request.user != profile_user:
            return render(request, "accounts/_profile_ratings_private.html", {})

        sort = request.GET.get("sort", "newest")
        if sort not in _SORT_ORDERS:
            sort = "newest"

        dish_type_slug = request.GET.get("dish_type", "")

        qs = RatingSubmission.objects.filter(user=profile_user)

        if dish_type_slug:
            if DishType.objects.filter(slug=dish_type_slug, is_active=True).exists():
                qs = qs.filter(dish__dish_type__slug=dish_type_slug)
            else:
                dish_type_slug = ""

        qs = qs.select_related("dish", "dish__venue", "dish__dish_type").order_by(_SORT_ORDERS[sort])

        dish_types = (
            DishType.objects
            .filter(dishes__rating_submissions__user=profile_user, is_active=True)
            .distinct()
            .order_by("name")
        )

        page_size = getattr(django_settings, "COMMUNITY_NOTES_PAGE_SIZE", 10)
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(request.GET.get("page", 1))

        return render(request, self.template_name, {
            "profile_user": profile_user,
            "page_obj": page_obj,
            "current_sort": sort,
            "current_dish_type": dish_type_slug,
            "dish_types": dish_types,
            "sort_options": [
                ("Newest", "newest"),
                ("Oldest", "oldest"),
                ("Highest", "highest"),
                ("Lowest", "lowest"),
            ],
        })


@login_required
def profile_settings(request):
    userprofile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"is_public": True}
    )
    if request.method == "POST":
        form = ProfileVisibilityForm(request.POST, instance=userprofile)
        if form.is_valid():
            form.save()
            logger.info(
                "accounts.visibility_changed user_id=%s is_public=%s",
                request.user.id,
                form.instance.is_public,
            )
            return redirect("profile", username=request.user.username)
    else:
        form = ProfileVisibilityForm(instance=userprofile)
    return render(request, "accounts/profile_settings.html", {"form": form})
