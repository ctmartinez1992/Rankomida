from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Dish, DishType, Venue
from ratings.models import CriteriaTemplate, RatingCriterionScore, RatingSubmission


class LeaderboardViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="ranker", email="ranker@example.com", password="pass"
        )
        self.dish_type, _ = DishType.objects.get_or_create(slug="francesinha", defaults={"name": "Francesinha"})
        venue = Venue.objects.create(name="Venue", slug="venue", city="Porto")
        self.dish_a = Dish.objects.create(
            name="Dish A", slug="dish-a", dish_type=self.dish_type, venue=venue
        )
        self.dish_b = Dish.objects.create(
            name="Dish B", slug="dish-b", dish_type=self.dish_type, venue=venue
        )
        self.criterion = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="sauce",
            label="Sauce",
            weight=Decimal("1.0"),
            min_score=Decimal("1.0"),
            max_score=Decimal("10.0"),
        )

    def _submit(self, dish, overall, criterion_score):
        sub = RatingSubmission.objects.create(
            dish=dish, user=self.user, overall_score=Decimal(str(overall))
        )
        RatingCriterionScore.objects.create(
            submission=sub, template=self.criterion, score=Decimal(str(criterion_score))
        )
        return sub

    def test_overall_ranking_order(self):
        self._submit(self.dish_a, 9.0, 8.0)
        self._submit(self.dish_b, 7.0, 6.0)

        response = self.client.get(reverse("leaderboard:by_dish_type", args=["francesinha"]))
        self.assertEqual(response.status_code, 200)
        entries = list(response.context["entries"])
        self.assertEqual(entries[0].pk, self.dish_a.pk)
        self.assertEqual(entries[1].pk, self.dish_b.pk)

    def test_criterion_ranking_order(self):
        self._submit(self.dish_a, 9.0, 5.0)
        self._submit(self.dish_b, 7.0, 9.0)

        url = reverse("leaderboard:by_dish_type", args=["francesinha"]) + "?criterion=sauce"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        entries = list(response.context["entries"])
        self.assertEqual(entries[0].pk, self.dish_b.pk, "Higher criterion score should rank first")
        self.assertEqual(entries[1].pk, self.dish_a.pk)

    def test_dishes_with_no_ratings_excluded(self):
        self._submit(self.dish_a, 8.0, 7.0)

        response = self.client.get(reverse("leaderboard:by_dish_type", args=["francesinha"]))
        self.assertEqual(response.status_code, 200)
        entry_pks = [e.pk for e in response.context["entries"]]
        self.assertIn(self.dish_a.pk, entry_pks)
        self.assertNotIn(self.dish_b.pk, entry_pks)

    def test_unknown_criterion_key_falls_back_to_overall(self):
        self._submit(self.dish_a, 9.0, 8.0)
        self._submit(self.dish_b, 7.0, 6.0)

        url = reverse("leaderboard:by_dish_type", args=["francesinha"]) + "?criterion=nonexistent"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        entries = list(response.context["entries"])
        self.assertEqual(entries[0].pk, self.dish_a.pk, "Should fall back to overall ranking")
        self.assertIsNone(response.context["current_criterion"])

    def test_criteria_tabs_present_on_dish_type_page(self):
        response = self.client.get(reverse("leaderboard:by_dish_type", args=["francesinha"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.criterion, response.context["criteria_templates"])

    def test_no_criteria_tabs_on_global_leaderboard(self):
        response = self.client.get(reverse("leaderboard:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["criteria_templates"]), [])

    def test_sort_score_annotation_present(self):
        self._submit(self.dish_a, 8.0, 7.0)
        response = self.client.get(reverse("leaderboard:by_dish_type", args=["francesinha"]))
        entry = response.context["entries"][0]
        self.assertTrue(hasattr(entry, "sort_score"))
        self.assertTrue(hasattr(entry, "rating_count"))
