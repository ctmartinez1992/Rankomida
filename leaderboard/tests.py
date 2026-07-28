from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from catalog.models import Dish, DishType, Venue
from ratings.models import CriteriaTemplate, RatingCriterionScore, RatingSubmission

from .models import DishAggregateScore
from .services import recompute_dish_aggregate


class LeaderboardComputationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ranker", email="ranker@example.com", password="password12345"
        )
        self.dish_type, _ = DishType.objects.get_or_create(
            slug="francesinha",
            defaults={"name": "Francesinha"},
        )
        venue = Venue.objects.create(name="Venue", slug="venue", city="Porto")
        self.dish_a = Dish.objects.create(
            name="Dish A",
            slug="dish-a",
            dish_type=self.dish_type,
            venue=venue,
        )
        self.dish_b = Dish.objects.create(
            name="Dish B",
            slug="dish-b",
            dish_type=self.dish_type,
            venue=venue,
        )
        self.criterion = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="sauce",
            label="Sauce",
            weight=Decimal("1.0"),
            min_score=Decimal("1.0"),
            max_score=Decimal("10.0"),
        )

    def _create_submission(self, dish, overall, criterion):
        submission = RatingSubmission.objects.create(
            dish=dish,
            user=self.user,
            overall_score=Decimal(str(overall)),
        )
        RatingCriterionScore.objects.create(
            submission=submission,
            template=self.criterion,
            score=Decimal(str(criterion)),
        )

    def test_higher_weighted_score_ranks_first(self):
        self._create_submission(self.dish_a, 9.0, 9.0)
        self._create_submission(self.dish_b, 7.0, 7.0)
        recompute_dish_aggregate(self.dish_a)
        recompute_dish_aggregate(self.dish_b)

        ordered = list(
            DishAggregateScore.objects.order_by("-composite_score", "-rating_count", "dish__name")
        )
        self.assertEqual(ordered[0].dish, self.dish_a)

    def test_recompute_command_is_deterministic(self):
        self._create_submission(self.dish_a, 8.0, 8.0)
        call_command("recompute_aggregates")
        first = DishAggregateScore.objects.get(dish=self.dish_a).composite_score
        call_command("recompute_aggregates")
        second = DishAggregateScore.objects.get(dish=self.dish_a).composite_score
        self.assertEqual(first, second)
