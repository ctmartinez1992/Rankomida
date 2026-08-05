from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegistrationForm
from .models import UserProfile
from ratings.models import RatingSubmission


class ProfileVisibilityForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["is_public"]
        labels = {"is_public": "Make my profile public"}


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
        return render(request, "accounts/profile_private.html", {"profile_user": profile_user})

    submissions = (
        RatingSubmission.objects
        .filter(user=profile_user)
        .select_related("dish", "dish__venue", "dish__dish_type")
        .order_by("-created_at")
    )
    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "userprofile": userprofile,
        "submissions": submissions,
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
            return redirect("profile", username=request.user.username)
    else:
        form = ProfileVisibilityForm(instance=userprofile)
    return render(request, "accounts/profile_settings.html", {"form": form})
