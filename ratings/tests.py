from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .templatetags.ratings_tags import score_as_stars
from .widgets import StarRatingField


class ScoreAsStarsFilterTests(TestCase):
    def test_whole_star(self):
        self.assertEqual(score_as_stars(Decimal("3")), "★★★☆☆")

    def test_half_star(self):
        self.assertEqual(score_as_stars(Decimal("3.5")), "★★★½☆")

    def test_minimum_score(self):
        self.assertEqual(score_as_stars(Decimal("1")), "★☆☆☆☆")

    def test_half_star_minimum(self):
        self.assertEqual(score_as_stars(Decimal("0.5")), "½☆☆☆☆")

    def test_maximum_score(self):
        self.assertEqual(score_as_stars(Decimal("5")), "★★★★★")

    def test_none_returns_dash(self):
        self.assertEqual(score_as_stars(None), "–")

    def test_zero_returns_dash(self):
        self.assertEqual(score_as_stars(0), "–")

    def test_out_of_range_above_returns_dash(self):
        self.assertEqual(score_as_stars(Decimal("7.5")), "–")

    def test_out_of_range_below_returns_dash(self):
        self.assertEqual(score_as_stars(Decimal("0")), "–")


class StarRatingFieldTests(TestCase):
    def setUp(self):
        self.field = StarRatingField(required=True)

    def test_valid_whole_values_accepted(self):
        for v in ["1", "2", "3", "4", "5"]:
            result = self.field.clean(v)
            self.assertEqual(result, Decimal(v))

    def test_half_star_minimum_accepted(self):
        result = self.field.clean("0.5")
        self.assertEqual(result, Decimal("0.5"))

    def test_valid_half_values_accepted(self):
        for v in ["1.5", "2.5", "3.5", "4.5"]:
            result = self.field.clean(v)
            self.assertEqual(result, Decimal(v))

    def test_returns_decimal(self):
        result = self.field.clean("3.5")
        self.assertIsInstance(result, Decimal)

    def test_out_of_range_rejected(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.field.clean("6")

    def test_non_half_step_rejected(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.field.clean("2.3")

    def test_zero_rejected(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.field.clean("0")

    def test_empty_required_raises(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.field.clean("")


from catalog.models import Dish, DishType, Venue

from .forms import RatingSubmissionForm
from .models import CriteriaTemplate, RatingCriterionScore, RatingSubmission


class RatingValidationTests(TestCase):
    def setUp(self):
        self.dish_type, _ = DishType.objects.get_or_create(
            slug="francesinha",
            defaults={"name": "Francesinha"},
        )
        self.venue = Venue.objects.create(name="Cafe A", slug="cafe-a", city="Porto")
        self.dish = Dish.objects.create(
            name="Classic Francesinha",
            slug="classic-francesinha",
            dish_type=self.dish_type,
            venue=self.venue,
        )
        self.criterion_a = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="sauce",
            label="Sauce",
            weight=Decimal("2.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )
        self.criterion_b = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="meat",
            label="Meat",
            weight=Decimal("1.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )

    def test_missing_required_criterion_is_invalid(self):
        form = RatingSubmissionForm(
            data={
                "overall_score": "4",
                f"criterion_{self.criterion_a.id}": "4.5",
            },
            dish=self.dish,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(f"criterion_{self.criterion_b.id}", form.errors)

    def test_out_of_range_criterion_is_invalid(self):
        form = RatingSubmissionForm(
            data={
                "overall_score": "4",
                f"criterion_{self.criterion_a.id}": "6",
                f"criterion_{self.criterion_b.id}": "3.5",
            },
            dish=self.dish,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(f"criterion_{self.criterion_a.id}", form.errors)


class AuthenticatedSubmissionIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", email="tester@example.com", password="password123"
        )
        self.dish_type, _ = DishType.objects.get_or_create(
            slug="francesinha",
            defaults={"name": "Francesinha"},
        )
        self.venue = Venue.objects.create(name="Cafe A", slug="cafe-a", city="Porto")
        self.dish = Dish.objects.create(
            name="Classic Francesinha",
            slug="classic-francesinha",
            dish_type=self.dish_type,
            venue=self.venue,
        )
        self.criterion = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="sauce",
            label="Sauce",
            weight=Decimal("1.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )

    def test_authenticated_submission_creates_rating(self):
        self.client.login(username="tester", password="password123")
        response = self.client.post(
            reverse("ratings:submit", kwargs={"slug": self.dish.slug}),
            {
                "overall_score": "4",
                f"criterion_{self.criterion.id}": "4.5",
            },
        )

        self.assertEqual(response.status_code, 302)
        submission = RatingSubmission.objects.get()
        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.overall_score, Decimal("4"))
        self.assertEqual(
            submission.criterion_scores.get(template=self.criterion).score, Decimal("4.5")
        )


class UniqueRatingPerUserTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="rater", email="rater@example.com", password="password123"
        )
        self.dish_type, _ = DishType.objects.get_or_create(
            slug="francesinha",
            defaults={"name": "Francesinha"},
        )
        self.venue = Venue.objects.create(name="Cafe B", slug="cafe-b", city="Porto")
        self.dish = Dish.objects.create(
            name="Spicy Francesinha",
            slug="spicy-francesinha",
            dish_type=self.dish_type,
            venue=self.venue,
        )
        self.criterion = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="heat",
            label="Heat",
            weight=Decimal("1.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )

    def _post_rating(self, overall, criterion_score):
        self.client.login(username="rater", password="password123")
        return self.client.post(
            reverse("ratings:submit", kwargs={"slug": self.dish.slug}),
            {
                "overall_score": str(overall),
                f"criterion_{self.criterion.id}": str(criterion_score),
            },
        )

    def test_second_submission_updates_not_duplicates(self):
        self._post_rating(3.5, 3)
        self._post_rating(4.5, 4)

        self.assertEqual(RatingSubmission.objects.filter(user=self.user, dish=self.dish).count(), 1)
        submission = RatingSubmission.objects.get(user=self.user, dish=self.dish)
        self.assertEqual(submission.overall_score, Decimal("4.5"))

    def test_criterion_scores_updated_on_revision(self):
        self._post_rating(3.5, 3)
        self._post_rating(4.5, 4)

        submission = RatingSubmission.objects.get(user=self.user, dish=self.dish)
        score = RatingCriterionScore.objects.get(submission=submission, template=self.criterion)
        self.assertEqual(score.score, Decimal("4"))

    def test_orphaned_scores_untouched_on_revision(self):
        """Criterion scores for deactivated templates are not deleted on update."""
        orphan_template = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="aroma",
            label="Aroma",
            weight=Decimal("1.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )
        submission = RatingSubmission.objects.create(
            user=self.user, dish=self.dish, overall_score=Decimal("3.5")
        )
        RatingCriterionScore.objects.create(
            submission=submission, template=self.criterion, score=Decimal("3")
        )
        RatingCriterionScore.objects.create(
            submission=submission, template=orphan_template, score=Decimal("2.5")
        )

        orphan_template.is_active = False
        orphan_template.save()
        self._post_rating(4.5, 4)

        submission.refresh_from_db()
        self.assertTrue(
            RatingCriterionScore.objects.filter(
                submission=submission, template=orphan_template
            ).exists()
        )

    def test_get_form_prefilled_with_existing_scores(self):
        self._post_rating(3.5, 3)
        self.client.login(username="rater", password="password123")
        response = self.client.get(
            reverse("ratings:submit", kwargs={"slug": self.dish.slug})
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.fields["overall_score"].initial, Decimal("3.5"))
        self.assertEqual(
            form.fields[f"criterion_{self.criterion.id}"].initial, Decimal("3")
        )

    def test_updated_at_changes_after_revision(self):
        self._post_rating(3.5, 3)
        first_submission = RatingSubmission.objects.get(user=self.user, dish=self.dish)
        first_updated_at = first_submission.updated_at

        self._post_rating(4.5, 4)
        second_submission = RatingSubmission.objects.get(user=self.user, dish=self.dish)

        self.assertGreaterEqual(second_submission.updated_at, first_updated_at)
