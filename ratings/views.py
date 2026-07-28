from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Dish
from leaderboard.services import recompute_dish_aggregate

from .forms import RatingSubmissionForm
from .models import RatingSubmission


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
            recompute_dish_aggregate(dish)
            return redirect("catalog:detail", slug=dish.slug)
    else:
        form = RatingSubmissionForm(dish=dish, submission=existing)

    return render(request, "ratings/rating_form.html", {"form": form, "dish": dish})
