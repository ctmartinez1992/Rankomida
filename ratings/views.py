import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Dish, SavedDish

from .forms import RatingSubmissionForm
from .models import RatingSubmission

logger = logging.getLogger(__name__)


@login_required
def submit_rating(request, slug):
    dish = get_object_or_404(
        Dish.objects.select_related("dish_type", "venue").filter(is_published=True), slug=slug
    )
    existing = RatingSubmission.objects.filter(user=request.user, dish=dish).first()

    if request.method == "POST":
        form = RatingSubmissionForm(request.POST, dish=dish, submission=existing)
        if form.is_valid():
            form.save(user=request.user)
            SavedDish.objects.filter(user=request.user, dish=dish).delete()
            return redirect("catalog:detail", type_slug=dish.dish_type.slug, slug=dish.slug)
        logger.warning(
            "rating.form_invalid user_id=%s dish_slug=%s errors=%s",
            request.user.id,
            dish.slug,
            form.errors,
        )
    else:
        form = RatingSubmissionForm(dish=dish, submission=existing)

    return render(request, "ratings/rating_form.html", {"form": form, "dish": dish})
