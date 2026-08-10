from decimal import Decimal
from io import BytesIO, StringIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from catalog.models import Dish, DishType, SavedDish, Venue, VenueLocation


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


class SavedDishTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(username="saver", password="password123")
        self.other = User.objects.create_user(username="other", password="password123")
        self.dish_type = DishType.objects.create(name="Save Type", slug="save-type", is_active=True)
        self.venue = Venue.objects.create(name="Save Venue", slug="save-venue", city="Porto")
        self.dish = Dish.objects.create(
            name="Save Dish",
            slug="save-dish",
            dish_type=self.dish_type,
            venue=self.venue,
            is_published=True,
        )
        self.unpublished = Dish.objects.create(
            name="Hidden Dish",
            slug="hidden-dish",
            dish_type=self.dish_type,
            venue=self.venue,
            is_published=False,
        )
        self.save_url = reverse("catalog:save", kwargs={"slug": self.dish.slug})
        self.unsave_url = reverse("catalog:unsave", kwargs={"slug": self.dish.slug})
        self.saved_list_url = reverse("catalog:saved")

    def test_save_requires_login(self):
        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertEqual(SavedDish.objects.count(), 0)

    def test_save_creates_unique_row_and_second_save_is_noop(self):
        self.client.login(username="saver", password="password123")
        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SavedDish.objects.filter(user=self.user, dish=self.dish).count(), 1)

        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SavedDish.objects.filter(user=self.user, dish=self.dish).count(), 1)

    def test_unsave_removes_row(self):
        SavedDish.objects.create(user=self.user, dish=self.dish)
        self.client.login(username="saver", password="password123")
        response = self.client.post(self.unsave_url, {"next": self.saved_list_url})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.saved_list_url)
        self.assertFalse(SavedDish.objects.filter(user=self.user, dish=self.dish).exists())

    def test_saved_list_requires_login(self):
        response = self.client.get(self.saved_list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_saved_list_shows_only_own_published_dishes(self):
        SavedDish.objects.create(user=self.user, dish=self.dish)
        SavedDish.objects.create(user=self.user, dish=self.unpublished)
        other_dish = Dish.objects.create(
            name="Other Dish",
            slug="other-dish",
            dish_type=self.dish_type,
            venue=self.venue,
            is_published=True,
        )
        SavedDish.objects.create(user=self.other, dish=other_dish)

        self.client.login(username="saver", password="password123")
        response = self.client.get(self.saved_list_url)
        self.assertEqual(response.status_code, 200)
        saved = list(response.context["saved_dishes"])
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].dish, self.dish)
        self.assertContains(response, "Save Dish")
        self.assertNotContains(response, "Hidden Dish")
        self.assertNotContains(response, "Other Dish")

    def test_rating_removes_saved_dish(self):
        from decimal import Decimal

        from ratings.models import CriteriaTemplate

        from config.recaptcha_test import VALID_CAPTCHA_POST, mock_recaptcha_valid

        SavedDish.objects.create(user=self.user, dish=self.dish)
        criterion = CriteriaTemplate.objects.create(
            dish_type=self.dish_type,
            key="taste",
            label="Taste",
            weight=Decimal("1.0"),
            min_score=Decimal("0.5"),
            max_score=Decimal("5.0"),
        )
        self.client.login(username="saver", password="password123")
        with mock_recaptcha_valid():
            response = self.client.post(
                reverse("ratings:submit", kwargs={"slug": self.dish.slug}),
                {
                    "overall_score": "4",
                    f"criterion_{criterion.id}": "4",
                    **VALID_CAPTCHA_POST,
                },
            )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SavedDish.objects.filter(user=self.user, dish=self.dish).exists())


def _place(place_id="ChIJsantiago", name="Café Santiago", **overrides):
    place = {
        "id": place_id,
        "displayName": {"text": name, "languageCode": "pt"},
        "formattedAddress": "Rua de Passos Manuel 226, 4000-382 Porto",
        "location": {"latitude": 41.146945, "longitude": -8.605215},
        "addressComponents": [
            {"longText": "226", "shortText": "226", "types": ["street_number"]},
            {"longText": "Porto", "shortText": "Porto", "types": ["locality", "political"]},
            {
                "longText": "Bonfim",
                "shortText": "Bonfim",
                "types": ["sublocality_level_1", "sublocality", "political"],
            },
            {"longText": "4000-382", "shortText": "4000-382", "types": ["postal_code"]},
        ],
        "businessStatus": "OPERATIONAL",
        "primaryType": "restaurant",
        "types": ["restaurant", "food"],
        "priceLevel": "PRICE_LEVEL_MODERATE",
        "regularOpeningHours": {"weekdayDescriptions": ["Monday: 12:00–23:00"]},
        "nationalPhoneNumber": "222 055 797",
        "websiteUri": "https://cafesantiago.pt/",
        "googleMapsUri": "https://maps.google.com/?cid=1",
        "rating": 4.3,
        "userRatingCount": 12000,
    }
    place.update(overrides)
    return place


def _search_returning(results_by_query):
    def _search(query, **kwargs):
        return iter(results_by_query.get(query, []))

    return _search


@override_settings(GOOGLE_MAPS_API_KEY="test-key")
class ImportGooglePlacesTests(TestCase):
    patch_target = "catalog.management.commands.import_google_places.search_text"

    def _run(self, results_by_query, *args):
        out, err = StringIO(), StringIO()
        queries = []
        for query in results_by_query:
            queries += ["--query", query]
        with mock.patch(self.patch_target, side_effect=_search_returning(results_by_query)):
            call_command("import_google_places", *queries, *args, stdout=out, stderr=err)
        return out.getvalue() + err.getvalue()

    def test_import_creates_unpublished_venue_with_mapped_fields(self):
        self._run({"francesinha porto": [_place()]})

        venue = Venue.objects.get()
        self.assertEqual(venue.name, "Café Santiago")
        self.assertEqual(venue.city, "Porto")
        self.assertFalse(venue.is_published)
        self.assertEqual(venue.source, Venue.SOURCE_GOOGLE)

        location = venue.locations.get()
        self.assertEqual(location.google_place_id, "ChIJsantiago")
        self.assertEqual(location.address, "Rua de Passos Manuel 226, 4000-382 Porto")
        self.assertEqual(location.latitude, Decimal("41.146945"))
        self.assertEqual(location.longitude, Decimal("-8.605215"))
        self.assertEqual(location.postal_code, "4000-382")
        self.assertEqual(location.neighbourhood, "Bonfim")
        self.assertEqual(location.business_status, "OPERATIONAL")
        self.assertEqual(location.phone, "222 055 797")
        self.assertEqual(location.website_url, "https://cafesantiago.pt/")
        self.assertEqual(location.price_level, "PRICE_LEVEL_MODERATE")
        self.assertEqual(location.primary_type, "restaurant")
        self.assertEqual(location.types, ["restaurant", "food"])
        self.assertEqual(location.google_rating, Decimal("4.3"))
        self.assertEqual(location.google_user_rating_count, 12000)
        self.assertIsNotNone(location.opening_hours)
        self.assertIsNotNone(location.last_synced_at)

    def test_rerun_updates_instead_of_duplicating(self):
        self._run({"francesinha porto": [_place()]})
        changed = _place(
            formattedAddress="Rua Nova 1, 4000-000 Porto",
            businessStatus="CLOSED_TEMPORARILY",
        )
        output = self._run({"francesinha porto": [changed]})

        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(VenueLocation.objects.count(), 1)
        location = VenueLocation.objects.get()
        self.assertEqual(location.address, "Rua Nova 1, 4000-000 Porto")
        self.assertEqual(location.business_status, "CLOSED_TEMPORARILY")
        self.assertIn("update", output)

    def test_rerun_preserves_staff_name_and_published_state(self):
        self._run({"francesinha porto": [_place()]})
        venue = Venue.objects.get()
        venue.name = "Santiago (curated)"
        venue.is_published = True
        venue.save()

        self._run({"francesinha porto": [_place()]})

        venue.refresh_from_db()
        self.assertEqual(venue.name, "Santiago (curated)")
        self.assertTrue(venue.is_published)

    def test_dry_run_writes_nothing(self):
        output = self._run({"francesinha porto": [_place()]}, "--dry-run")
        self.assertEqual(Venue.objects.count(), 0)
        self.assertEqual(VenueLocation.objects.count(), 0)
        self.assertIn("Dry run", output)
        self.assertIn("Would create", output)

    def test_slug_collision_produces_distinct_slug(self):
        Venue.objects.create(name="Something else", slug="cafe-santiago", city="Porto")

        self._run({"francesinha porto": [_place()]})

        imported = Venue.objects.get(source=Venue.SOURCE_GOOGLE)
        self.assertEqual(imported.slug, "cafe-santiago-2")

    def test_place_in_two_queries_is_imported_once(self):
        shared = _place()
        self._run({"francesinha porto": [shared], "prego porto": [shared]})

        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(VenueLocation.objects.count(), 1)

    def test_missing_api_key_aborts_without_requests(self):
        with override_settings(GOOGLE_MAPS_API_KEY=""):
            with mock.patch(self.patch_target) as search:
                with self.assertRaises(CommandError) as ctx:
                    call_command("import_google_places", stdout=StringIO())
        self.assertIn("GOOGLE_MAPS_API_KEY", str(ctx.exception))
        search.assert_not_called()
        self.assertEqual(Venue.objects.count(), 0)

    def test_malformed_place_is_skipped_and_batch_continues(self):
        malformed_name = _place(place_id="ChIJbroken", displayName={})
        no_id = {"displayName": {"text": "No identity"}}
        output = self._run(
            {"francesinha porto": [malformed_name, no_id, _place(place_id="ChIJgood", name="Bufete Fase")]}
        )

        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(Venue.objects.get().name, "Bufete Fase")
        self.assertIn("skipped 2", output)

    def test_query_failure_does_not_stop_other_queries(self):
        from catalog.services.google_places import PlacesError

        def _search(query, **kwargs):
            if query == "francesinha porto":
                raise PlacesError("boom")
            return iter([_place(place_id="ChIJprego", name="Prego House")])

        out, err = StringIO(), StringIO()
        with mock.patch(self.patch_target, side_effect=_search):
            call_command(
                "import_google_places",
                "--query", "francesinha porto",
                "--query", "prego porto",
                stdout=out,
                stderr=err,
            )

        self.assertIn("Query failed", err.getvalue())
        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(Venue.objects.get().name, "Prego House")


class VenuePublicationVisibilityTests(TestCase):
    def setUp(self):
        self.published = Venue.objects.create(
            name="Published Venue", slug="published-venue", city="Porto"
        )
        self.hidden = Venue.objects.create(
            name="Hidden Venue",
            slug="hidden-venue",
            city="Braga",
            is_published=False,
            source=Venue.SOURCE_GOOGLE,
        )

    def test_new_venue_defaults_to_published(self):
        self.assertTrue(self.published.is_published)
        self.assertEqual(self.published.source, Venue.SOURCE_MANUAL)

    def test_venue_list_excludes_unpublished(self):
        response = self.client.get(reverse("catalog:venue_list"))
        self.assertEqual(response.status_code, 200)
        names = [v.name for v in response.context["venues"]]
        self.assertIn("Published Venue", names)
        self.assertNotIn("Hidden Venue", names)

    def test_city_options_ignore_unpublished(self):
        response = self.client.get(reverse("catalog:venue_list"))
        cities = list(response.context["cities"])
        self.assertIn("Porto", cities)
        self.assertNotIn("Braga", cities)

    def test_search_and_sort_respect_publication(self):
        response = self.client.get(
            reverse("catalog:venue_list"), {"q": "Venue", "sort": "dishes"}
        )
        names = [v.name for v in response.context["venues"]]
        self.assertEqual(names, ["Published Venue"])

    def test_unpublished_venue_detail_returns_404(self):
        response = self.client.get(
            reverse("catalog:venue_detail", kwargs={"slug": "hidden-venue"})
        )
        self.assertEqual(response.status_code, 404)

    def test_published_venue_detail_is_served(self):
        response = self.client.get(
            reverse("catalog:venue_detail", kwargs={"slug": "published-venue"})
        )
        self.assertEqual(response.status_code, 200)

    def test_publishing_reveals_the_venue(self):
        self.hidden.is_published = True
        self.hidden.save()

        response = self.client.get(reverse("catalog:venue_list"))
        names = [v.name for v in response.context["venues"]]
        self.assertIn("Hidden Venue", names)
        detail = self.client.get(
            reverse("catalog:venue_detail", kwargs={"slug": "hidden-venue"})
        )
        self.assertEqual(detail.status_code, 200)
