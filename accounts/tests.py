from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import UserProfile
from catalog.models import Dish, DishType, Venue
from ratings.models import RatingSubmission


def _make_dish(suffix=""):
    dt = DishType.objects.get_or_create(name=f"Type{suffix}", slug=f"type{suffix}", is_active=True)[0]
    venue = Venue.objects.get_or_create(name=f"Venue{suffix}", slug=f"venue{suffix}", city="Porto")[0]
    return Dish.objects.get_or_create(
        name=f"Dish{suffix}", slug=f"dish{suffix}", dish_type=dt, venue=venue, is_published=True,
    )[0]


class ProfileRatingsFragmentViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw")
        UserProfile.objects.get_or_create(user=self.owner, defaults={"is_public": True})
        self.url = "/accounts/profile/owner/ratings/"

        for i in range(15):
            dish = _make_dish(str(i))
            RatingSubmission.objects.create(
                dish=dish, user=self.owner, overall_score=1.0 + (i % 5) * 0.5,
            )

    def test_default_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_default_page_shows_10_results(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["page_obj"].object_list), 10)

    def test_second_page_shows_remaining(self):
        response = self.client.get(self.url + "?sort=newest&page=2")
        self.assertEqual(len(response.context["page_obj"].object_list), 5)

    def test_sort_newest(self):
        response = self.client.get(self.url + "?sort=newest")
        self.assertEqual(response.context["current_sort"], "newest")

    def test_sort_oldest(self):
        response = self.client.get(self.url + "?sort=oldest")
        self.assertEqual(response.context["current_sort"], "oldest")

    def test_sort_highest(self):
        response = self.client.get(self.url + "?sort=highest")
        self.assertEqual(response.context["current_sort"], "highest")

    def test_sort_lowest(self):
        response = self.client.get(self.url + "?sort=lowest")
        self.assertEqual(response.context["current_sort"], "lowest")

    def test_invalid_sort_falls_back_to_newest(self):
        response = self.client.get(self.url + "?sort=bogus")
        self.assertEqual(response.context["current_sort"], "newest")

    def test_out_of_range_page_returns_last_page(self):
        response = self.client.get(self.url + "?page=999")
        self.assertEqual(response.status_code, 200)

    def test_unknown_user_returns_404(self):
        response = self.client.get("/accounts/profile/nobody/ratings/")
        self.assertEqual(response.status_code, 404)

    def test_private_profile_blocked_for_anonymous(self):
        UserProfile.objects.filter(user=self.owner).update(is_public=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("page_obj", response.context)

    def test_private_profile_accessible_to_owner(self):
        UserProfile.objects.filter(user=self.owner).update(is_public=False)
        self.client.login(username="owner", password="pw")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)


class ProfileRatingsDishTypeFilterTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="filterowner", password="testpass")
        UserProfile.objects.get_or_create(user=self.owner, defaults={"is_public": True})
        self.url = "/accounts/profile/filterowner/ratings/"

        self.dt_a = DishType.objects.create(name="TypeA", slug="type-a", is_active=True)
        self.dt_b = DishType.objects.create(name="TypeB", slug="type-b", is_active=True)
        venue = Venue.objects.create(name="Venue", slug="venue-filter", city="Porto")

        self.dish_a = Dish.objects.create(
            name="DishA", slug="dish-a", dish_type=self.dt_a, venue=venue, is_published=True
        )
        self.dish_b = Dish.objects.create(
            name="DishB", slug="dish-b", dish_type=self.dt_b, venue=venue, is_published=True
        )
        RatingSubmission.objects.create(dish=self.dish_a, user=self.owner, overall_score=3.0)
        RatingSubmission.objects.create(dish=self.dish_b, user=self.owner, overall_score=4.0)

    def test_no_dish_type_param_returns_all_ratings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 2)

    def test_dish_type_filter_returns_only_matching_ratings(self):
        response = self.client.get(self.url + "?dish_type=type-a")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(response.context["page_obj"].object_list[0].dish, self.dish_a)

    def test_unknown_dish_type_slug_falls_back_to_all(self):
        response = self.client.get(self.url + "?dish_type=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 2)
        self.assertEqual(response.context["current_dish_type"], "")

    def test_dish_types_context_contains_only_rated_types(self):
        DishType.objects.create(name="TypeC", slug="type-c", is_active=True)
        response = self.client.get(self.url)
        slugs = [dt.slug for dt in response.context["dish_types"]]
        self.assertIn("type-a", slugs)
        self.assertIn("type-b", slugs)
        self.assertNotIn("type-c", slugs)

    def test_filter_bar_hidden_when_only_one_dish_type(self):
        RatingSubmission.objects.filter(dish=self.dish_b).delete()
        response = self.client.get(self.url)
        self.assertNotContains(response, "dish_type=type-a")

    def test_current_dish_type_in_context(self):
        response = self.client.get(self.url + "?dish_type=type-b")
        self.assertEqual(response.context["current_dish_type"], "type-b")
