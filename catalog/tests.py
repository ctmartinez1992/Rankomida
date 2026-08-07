from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from catalog.models import Dish, DishType, Venue


def _photo(name="test.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (1, 1), color=(255, 0, 0)).save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class PhotoAttributionModelTests(TestCase):
    def test_dish_saves_photo_without_attribution(self):
        dish_type = DishType.objects.create(name="Test Type A", slug="test-type-a")
        venue = Venue.objects.create(name="Test Venue A", slug="test-venue-a", city="Porto")
        dish = Dish.objects.create(
            name="Classic A",
            slug="classic-a",
            dish_type=dish_type,
            venue=venue,
            photo=_photo(),
        )
        dish.refresh_from_db()
        self.assertTrue(dish.photo)
        self.assertEqual(dish.photo_credit, "")
        self.assertEqual(dish.photo_source_url, "")

    def test_dish_persists_credit_and_source_url(self):
        dish_type = DishType.objects.create(name="Test Type B", slug="test-type-b")
        venue = Venue.objects.create(name="Test Venue B", slug="test-venue-b", city="Porto")
        dish = Dish.objects.create(
            name="Classic B",
            slug="classic-b",
            dish_type=dish_type,
            venue=venue,
            photo=_photo(),
            photo_credit="Photo: Example",
            photo_source_url="https://example.com/photo",
        )
        dish.refresh_from_db()
        self.assertEqual(dish.photo_credit, "Photo: Example")
        self.assertEqual(dish.photo_source_url, "https://example.com/photo")


class PhotoAttributionDisplayTests(TestCase):
    def test_dish_detail_shows_hover_attribution_link(self):
        dish_type = DishType.objects.create(name="Test Type C", slug="test-type-c")
        venue = Venue.objects.create(name="Test Venue C", slug="test-venue-c", city="Porto")
        Dish.objects.create(
            name="Classic C",
            slug="classic-c",
            dish_type=dish_type,
            venue=venue,
            photo=_photo(),
            photo_credit="Photo: Example",
            photo_source_url="https://example.com/photo",
        )
        response = self.client.get("/dishes/test-type-c/classic-c/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="photo-with-source"')
        self.assertContains(response, 'href="https://example.com/photo"')
        self.assertContains(response, "Photo: Example")
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')

    def test_dish_detail_without_attribution_has_no_overlay(self):
        dish_type = DishType.objects.create(name="Test Type D", slug="test-type-d")
        venue = Venue.objects.create(name="Test Venue D", slug="test-venue-d", city="Porto")
        Dish.objects.create(
            name="Classic D",
            slug="classic-d",
            dish_type=dish_type,
            venue=venue,
            photo=_photo(),
        )
        response = self.client.get("/dishes/test-type-d/classic-d/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="detail-photo"')
        self.assertNotContains(response, 'class="photo-with-source"')
        self.assertNotContains(response, 'class="photo-source-overlay"')


class CommunityNotesFragmentViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from ratings.models import RatingSubmission

        User = get_user_model()
        self.dish_type = DishType.objects.create(name="Frag Type", slug="frag-type", is_active=True)
        self.venue = Venue.objects.create(name="Frag Venue", slug="frag-venue", city="Porto")
        self.dish = Dish.objects.create(
            name="Frag Dish", slug="frag-dish", dish_type=self.dish_type,
            venue=self.venue, is_published=True,
        )
        self.url = f"/dishes/frag-type/frag-dish/notes/"

        for i in range(15):
            user = User.objects.create_user(username=f"user{i}", password="pw")
            RatingSubmission.objects.create(
                dish=self.dish, user=user,
                overall_score=1.0 + (i % 5) * 0.5,
            )

    def test_default_sort_returns_200(self):
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_sort"], "newest")

    def test_sort_oldest(self):
        response = self.client.get(self.url + "?sort=oldest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_sort"], "oldest")

    def test_sort_highest(self):
        response = self.client.get(self.url + "?sort=highest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_sort"], "highest")

    def test_sort_lowest(self):
        response = self.client.get(self.url + "?sort=lowest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_sort"], "lowest")

    def test_invalid_sort_falls_back_to_newest(self):
        response = self.client.get(self.url + "?sort=invalid")
        self.assertEqual(response.context["current_sort"], "newest")

    def test_out_of_range_page_returns_last_page(self):
        response = self.client.get(self.url + "?page=999")
        self.assertEqual(response.status_code, 200)

    def test_unknown_dish_returns_404(self):
        response = self.client.get("/dishes/frag-type/does-not-exist/notes/")
        self.assertEqual(response.status_code, 404)


class DishDetailRatingSummaryTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from ratings.models import RatingSubmission

        User = get_user_model()
        self.dish_type = DishType.objects.create(name="Summary Type", slug="summary-type", is_active=True)
        self.venue = Venue.objects.create(name="Summary Venue", slug="summary-venue", city="Porto")
        self.dish = Dish.objects.create(
            name="Summary Dish", slug="summary-dish", dish_type=self.dish_type,
            venue=self.venue, is_published=True,
        )
        self.url = "/dishes/summary-type/summary-dish/"
        self.User = User
        self.RatingSubmission = RatingSubmission

    def test_avg_score_and_rating_count_with_submissions(self):
        from decimal import Decimal
        user1 = self.User.objects.create_user(username="rater1", password="testpass")
        user2 = self.User.objects.create_user(username="rater2", password="testpass")
        self.RatingSubmission.objects.create(dish=self.dish, user=user1, overall_score=Decimal("4.0"))
        self.RatingSubmission.objects.create(dish=self.dish, user=user2, overall_score=Decimal("3.0"))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        dish = response.context["dish"]
        self.assertEqual(dish.rating_count, 2)
        self.assertAlmostEqual(float(dish.avg_score), 3.5)

    def test_avg_score_is_none_and_rating_count_is_zero_without_submissions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        dish = response.context["dish"]
        self.assertEqual(dish.rating_count, 0)
        self.assertIsNone(dish.avg_score)
