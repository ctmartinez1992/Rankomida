from decimal import Decimal

from django import forms
from django.db import transaction

from catalog.models import Dish, VenueLocation
from .models import RatingCriterionScore, RatingSubmission


class RatingSubmissionForm(forms.Form):
    overall_score = forms.DecimalField(min_value=Decimal("1.0"), max_value=Decimal("10.0"))
    comment = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Notes (optional)",
    )

    def __init__(self, *args, dish: Dish, submission: RatingSubmission | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dish = dish
        self.submission = submission
        self.criteria_templates = list(
            dish.dish_type.criteria_templates.filter(is_active=True).order_by("key")
        )

        if submission is not None:
            self.fields["overall_score"].initial = submission.overall_score
            self.fields["comment"].initial = submission.comment
            existing_scores = {
                cs.template_id: cs.score
                for cs in submission.criterion_scores.select_related("template")
            }
        else:
            existing_scores = {}

        for template in self.criteria_templates:
            self.fields[self._field_name(template.id)] = forms.DecimalField(
                label=template.label,
                min_value=template.min_score,
                max_value=template.max_score,
                required=template.is_required,
                initial=existing_scores.get(template.id),
            )

        # Venue location field — adapt to number of locations
        locations = list(dish.venue.locations.all())
        if len(locations) == 0:
            pass  # omit entirely
        elif len(locations) == 1:
            self.fields["venue_location"] = forms.ModelChoiceField(
                queryset=VenueLocation.objects.filter(pk=locations[0].pk),
                required=False,
                label="Location",
                widget=forms.HiddenInput(),
                initial=locations[0],
            )
        else:
            initial_location = submission.venue_location if submission is not None else None
            self.fields["venue_location"] = forms.ModelChoiceField(
                queryset=dish.venue.locations.all(),
                required=False,
                label="Location (optional)",
                empty_label="— select location (optional) —",
                initial=initial_location,
            )

    @staticmethod
    def _field_name(template_id: int) -> str:
        return f"criterion_{template_id}"

    @transaction.atomic
    def save(self, user):
        defaults = {
            "overall_score": self.cleaned_data["overall_score"],
            "comment": self.cleaned_data["comment"],
        }
        if "venue_location" in self.fields:
            defaults["venue_location"] = self.cleaned_data.get("venue_location")

        submission, _ = RatingSubmission.objects.update_or_create(
            user=user,
            dish=self.dish,
            defaults=defaults,
        )

        for template in self.criteria_templates:
            score_value = self.cleaned_data[self._field_name(template.id)]
            score_obj, _ = RatingCriterionScore.objects.update_or_create(
                submission=submission,
                template=template,
                defaults={"score": score_value},
            )
            score_obj.full_clean()

        return submission
