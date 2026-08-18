from decimal import Decimal
from io import BytesIO, StringIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from catalog.models import Dish, DishType, SavedDish, Venue, VenueLocation
from catalog.templatetags.catalog_tags import (
    business_status_label,
    humanize_place_type,
    location_heading,
    price_level_display,
    public_place_types,
    tel_href,
    weekday_hours,
)


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


# ---------------------------------------------------------------------------
# RequestBudget unit tests
# ---------------------------------------------------------------------------

class RequestBudgetTests(TestCase):
    """Unit tests for google_places.RequestBudget."""

    def setUp(self):
        from catalog.services.google_places import RequestBudget
        self.RequestBudget = RequestBudget

    def test_consume_decrements_correctly(self):
        b = self.RequestBudget(5)
        self.assertTrue(b.consume(3))
        self.assertEqual(b.used, 3)
        self.assertTrue(b.consume(2))
        self.assertEqual(b.used, 5)

    def test_consume_returns_false_when_exhausted(self):
        b = self.RequestBudget(2)
        self.assertTrue(b.consume(2))
        self.assertFalse(b.consume(1))
        self.assertEqual(b.used, 2)  # not incremented on failure

    def test_partial_consume_refused_when_would_exceed(self):
        b = self.RequestBudget(3)
        b.consume(2)
        self.assertFalse(b.consume(2))  # 2+2 > 3

    def test_zero_limit_means_unlimited(self):
        b = self.RequestBudget(0)
        for _ in range(1000):
            self.assertTrue(b.consume(1))
        self.assertEqual(b.used, 1000)

    def test_exhausted_property(self):
        b = self.RequestBudget(2)
        self.assertFalse(b.exhausted)
        b.consume(2)
        self.assertTrue(b.exhausted)

    def test_exhausted_false_for_unlimited(self):
        b = self.RequestBudget(0)
        b.consume(9999)
        self.assertFalse(b.exhausted)


# ---------------------------------------------------------------------------
# fetch_photo service tests
# ---------------------------------------------------------------------------

class FetchPhotoTests(TestCase):
    """Unit tests for google_places.fetch_photo()."""

    def setUp(self):
        from catalog.services.google_places import fetch_photo, PlacesError
        self.fetch_photo = fetch_photo
        self.PlacesError = PlacesError

    def _make_session(self, meta_status=200, meta_json=None, img_status=200, img_content=b"IMGDATA", network_error=False):
        session = mock.MagicMock()
        if network_error:
            session.get.side_effect = __import__('requests').RequestException("network fail")
            return session
        meta_resp = mock.MagicMock()
        meta_resp.status_code = meta_status
        if meta_json is not None:
            meta_resp.json.return_value = meta_json
        else:
            meta_resp.json.return_value = {"photoUri": "https://photos.example.com/img.jpg"}
        meta_resp.text = "error body"

        img_resp = mock.MagicMock()
        img_resp.status_code = img_status
        img_resp.content = img_content

        session.get.side_effect = [meta_resp, img_resp]
        return session

    def test_success_returns_image_bytes(self):
        session = self._make_session(img_content=b"FAKEIMAGE")
        result = self.fetch_photo("places/X/photos/Y", api_key="key", session=session)
        self.assertEqual(result, b"FAKEIMAGE")

    def test_non_200_meta_raises_places_error(self):
        session = self._make_session(meta_status=403)
        with self.assertRaises(self.PlacesError):
            self.fetch_photo("places/X/photos/Y", api_key="key", session=session)

    def test_network_error_raises_places_error(self):
        session = self._make_session(network_error=True)
        with self.assertRaises(self.PlacesError):
            self.fetch_photo("places/X/photos/Y", api_key="key", session=session)

    def test_missing_photo_uri_raises_places_error(self):
        session = self._make_session(meta_json={"something": "else"})
        with self.assertRaises(self.PlacesError):
            self.fetch_photo("places/X/photos/Y", api_key="key", session=session)

    def test_non_200_image_download_raises_places_error(self):
        session = self._make_session(img_status=500)
        with self.assertRaises(self.PlacesError):
            self.fetch_photo("places/X/photos/Y", api_key="key", session=session)


# ---------------------------------------------------------------------------
# import_google_places photo integration tests
# ---------------------------------------------------------------------------

def _place_with_photo(**overrides):
    place = _place(**overrides)
    place["photos"] = [{"name": "places/ChIJsantiago/photos/AXCitest"}]
    return place


@override_settings(GOOGLE_MAPS_API_KEY="test-key")
class ImportGooglePlacesPhotoTests(TestCase):
    """Tests for photo fetching behaviour added to the import command."""

    patch_search = "catalog.management.commands.import_google_places.search_text"
    patch_fetch = "catalog.management.commands.import_google_places.fetch_photo"

    def _run(self, results_by_query, fetch_return=b"IMGDATA", fetch_side_effect=None, extra_args=()):
        out, err = StringIO(), StringIO()
        queries = []
        for query in results_by_query:
            queries += ["--query", query]
        with mock.patch(self.patch_search, side_effect=_search_returning(results_by_query)):
            fetch_kwargs = {}
            if fetch_side_effect is not None:
                fetch_kwargs["side_effect"] = fetch_side_effect
            else:
                fetch_kwargs["return_value"] = fetch_return
            with mock.patch(self.patch_fetch, **fetch_kwargs) as mock_fetch:
                call_command("import_google_places", *queries, *extra_args, stdout=out, stderr=err)
        return out.getvalue() + err.getvalue(), mock_fetch

    def _tiny_png(self):
        buf = BytesIO()
        img = Image.new("RGB", (1, 1), color=(255, 0, 0))
        img.save(buf, format="JPEG")
        return buf.getvalue()

    def test_new_venue_with_photo_saves_photo_credit_source_url(self):
        image_bytes = self._tiny_png()
        self._run({"q": [_place_with_photo()]}, fetch_return=image_bytes)

        venue = Venue.objects.get()
        self.assertTrue(bool(venue.photo))
        self.assertEqual(venue.photo_credit, "Google Maps")
        self.assertEqual(venue.photo_source_url, "https://maps.google.com/?cid=1")

    def test_new_venue_without_photo_metadata_saves_no_photo(self):
        self._run({"q": [_place()]})

        venue = Venue.objects.get()
        self.assertFalse(bool(venue.photo))
        self.assertEqual(venue.photo_credit, "")
        self.assertEqual(venue.photo_source_url, "")

    def test_existing_venue_with_photo_skips_fetch(self):
        from django.core.files.base import ContentFile
        image_bytes = self._tiny_png()
        self._run({"q": [_place_with_photo()]}, fetch_return=image_bytes)

        venue = Venue.objects.get()
        self.assertTrue(bool(venue.photo))

        _, mock_fetch = self._run({"q": [_place_with_photo()]}, fetch_return=image_bytes)
        # fetch_photo must NOT be called on the re-sync (venue already has photo)
        mock_fetch.assert_not_called()

    def test_photo_fetch_failure_logs_warning_and_does_not_abort(self):
        from catalog.services.google_places import PlacesError
        _, mock_fetch = self._run(
            {"q": [_place_with_photo()]},
            fetch_side_effect=PlacesError("fail"),
        )

        venue = Venue.objects.get()
        self.assertFalse(bool(venue.photo))
        mock_fetch.assert_called_once()

    def test_dry_run_does_not_call_fetch_photo(self):
        _, mock_fetch = self._run({"q": [_place_with_photo()]}, extra_args=("--dry-run",))
        mock_fetch.assert_not_called()
        self.assertEqual(Venue.objects.count(), 0)

    def test_max_requests_limit_stops_photo_fetch_after_budget_exhausted(self):
        """With --max-requests 3, first search page (1) + first photo (2) = 3, second photo refused."""
        image_bytes = self._tiny_png()
        place_a = _place_with_photo(place_id="ChIJa", name="Venue A")
        place_b = _place_with_photo(place_id="ChIJb", name="Venue B")
        # Budget: 1 search page + 2 photo requests = 3; second photo needs 2 more → refused
        self._run({"q": [place_a, place_b]}, fetch_return=image_bytes, extra_args=("--max-requests", "3"))

        self.assertEqual(Venue.objects.count(), 2)
        venues = {v.name: v for v in Venue.objects.all()}
        self.assertTrue(bool(venues["Venue A"].photo))
        self.assertFalse(bool(venues["Venue B"].photo))

    def test_max_requests_zero_means_unlimited(self):
        """--max-requests 0 should not restrict fetches."""
        image_bytes = self._tiny_png()
        place_a = _place_with_photo(place_id="ChIJa", name="Venue A")
        place_b = _place_with_photo(place_id="ChIJb", name="Venue B")
        self._run({"q": [place_a, place_b]}, fetch_return=image_bytes, extra_args=("--max-requests", "0"))

        venues = {v.name: v for v in Venue.objects.all()}
        self.assertTrue(bool(venues["Venue A"].photo))
        self.assertTrue(bool(venues["Venue B"].photo))

    def test_venues_beyond_request_limit_are_still_created(self):
        """Venues whose photo fetch is refused by budget are still imported as venue+location."""
        image_bytes = self._tiny_png()
        place_a = _place_with_photo(place_id="ChIJa", name="Venue A")
        place_b = _place_with_photo(place_id="ChIJb", name="Venue B")
        self._run({"q": [place_a, place_b]}, fetch_return=image_bytes, extra_args=("--max-requests", "3"))

        self.assertEqual(Venue.objects.count(), 2)
        self.assertEqual(VenueLocation.objects.count(), 2)


class MergeVenuesAdminActionTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from ratings.models import RatingSubmission

        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.client.force_login(self.admin_user)
        self.RatingSubmission = RatingSubmission

        self.dish_type = DishType.objects.create(name="Tacos", slug="tacos")

        self.venue_a = Venue.objects.create(name="El Burrito", slug="el-burrito-a", city="Palermo")
        self.venue_b = Venue.objects.create(name="El Burrito", slug="el-burrito-b", city="SoHo")
        self.venue_c = Venue.objects.create(name="El Burrito", slug="el-burrito-c", city="Centro")

        self.loc_a = VenueLocation.objects.create(venue=self.venue_a, city="Palermo")
        self.loc_b = VenueLocation.objects.create(venue=self.venue_b, city="SoHo")

        self.dish_a = Dish.objects.create(
            name="Classic Taco", slug="classic-taco-a", dish_type=self.dish_type, venue=self.venue_a
        )
        self.dish_b = Dish.objects.create(
            name="Classic Taco", slug="classic-taco-b", dish_type=self.dish_type, venue=self.venue_b
        )
        self.dish_c = Dish.objects.create(
            name="Burrito Bowl", slug="burrito-bowl", dish_type=self.dish_type, venue=self.venue_b
        )

        self.user1 = User.objects.create_user(username="user1", password="pw")
        self.user2 = User.objects.create_user(username="user2", password="pw")

    def _trigger_action(self, venue_ids):
        """POST the admin changelist action to trigger the merge redirect."""
        return self.client.post(
            reverse("admin:catalog_venue_changelist"),
            {
                "action": "merge_venues",
                "_selected_action": venue_ids,
            },
            follow=False,
        )

    def _confirm_merge(self, selected_ids, survivor_id):
        """POST the confirmation form."""
        data = {
            "survivor_id": survivor_id,
            "selected_ids": selected_ids,
        }
        return self.client.post(
            reverse("admin:catalog_venue_merge"),
            data,
            follow=False,
        )

    # --- 4.5: single venue guard ---

    def test_single_venue_guard(self):
        response = self._trigger_action([self.venue_a.pk])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("admin:catalog_venue_changelist"), fetch_redirect_response=False)
        # Venues unchanged
        self.assertEqual(Venue.objects.count(), 3)

    # --- 4.1: happy path (no dish name conflicts) ---

    def test_happy_path_no_conflicts(self):
        """3 venues merged; dish_a (unique to venue_a) and dish_c (unique to venue_b) reassigned."""
        # dish_b shares name with dish_a — give them unique names for this test
        self.dish_a.name = "Unique Dish A"
        self.dish_a.save()
        self.dish_b.name = "Unique Dish B"
        self.dish_b.save()

        self._trigger_action([self.venue_a.pk, self.venue_b.pk, self.venue_c.pk])
        self._confirm_merge(
            [self.venue_a.pk, self.venue_b.pk, self.venue_c.pk],
            self.venue_a.pk,
        )

        # Only survivor remains
        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(Venue.objects.get().pk, self.venue_a.pk)

        # Locations reassigned and named after their original venue
        self.loc_a.refresh_from_db()
        self.loc_b.refresh_from_db()
        self.assertEqual(self.loc_b.venue, self.venue_a)
        self.assertEqual(self.loc_a.name, self.venue_a.name)
        self.assertEqual(self.loc_b.name, self.venue_b.name)

        # Dishes reassigned to survivor
        self.dish_a.refresh_from_db()
        self.dish_b.refresh_from_db()
        self.dish_c.refresh_from_db()
        self.assertEqual(self.dish_a.venue, self.venue_a)
        self.assertEqual(self.dish_b.venue, self.venue_a)
        self.assertEqual(self.dish_c.venue, self.venue_a)

    def test_location_name_already_set_is_not_overwritten(self):
        """If a VenueLocation already has a name, it should not be overwritten."""
        self.loc_b.name = "My Custom Name"
        self.loc_b.save()

        self._trigger_action([self.venue_a.pk, self.venue_b.pk])
        self._confirm_merge([self.venue_a.pk, self.venue_b.pk], self.venue_a.pk)

        self.loc_b.refresh_from_db()
        self.assertEqual(self.loc_b.name, "My Custom Name")

    def test_new_name_applied_to_survivor(self):
        """Providing new_name in the POST renames the surviving venue."""
        data = {
            "survivor_id": self.venue_a.pk,
            "selected_ids": [self.venue_a.pk, self.venue_b.pk],
            "new_name": "El Burrito Porto",
        }
        self._trigger_action([self.venue_a.pk, self.venue_b.pk])
        self.client.post(reverse("admin:catalog_venue_merge"), data, follow=False)

        self.venue_a.refresh_from_db()
        self.assertEqual(self.venue_a.name, "El Burrito Porto")
        # Slug unchanged
        self.assertEqual(self.venue_a.slug, "el-burrito-a")

    # --- 4.2: dish name conflict with rating merge ---

    def test_dish_name_conflict_rating_reassignment(self):
        """dish_a (survivor) and dish_b (non-survivor) share the name 'Classic Taco'.
        user1 only rated dish_b → submission reassigned to dish_a.
        user2 rated both → non-survivor submission deleted, survivor kept."""
        from ratings.models import RatingSubmission

        sub_user1 = RatingSubmission.objects.create(
            dish=self.dish_b, user=self.user1, overall_score=Decimal("4.0")
        )
        sub_user2_survivor = RatingSubmission.objects.create(
            dish=self.dish_a, user=self.user2, overall_score=Decimal("3.0")
        )
        sub_user2_nonsurvivor = RatingSubmission.objects.create(
            dish=self.dish_b, user=self.user2, overall_score=Decimal("5.0")
        )

        self._trigger_action([self.venue_a.pk, self.venue_b.pk])
        self._confirm_merge([self.venue_a.pk, self.venue_b.pk], self.venue_a.pk)

        # dish_b deleted (collapsed into dish_a)
        self.assertFalse(Dish.objects.filter(pk=self.dish_b.pk).exists())

        # user1's submission reassigned to dish_a
        sub_user1.refresh_from_db()
        self.assertEqual(sub_user1.dish, self.dish_a)

        # user2's survivor submission preserved
        sub_user2_survivor.refresh_from_db()
        self.assertEqual(sub_user2_survivor.dish, self.dish_a)

        # user2's non-survivor submission deleted
        self.assertFalse(RatingSubmission.objects.filter(pk=sub_user2_nonsurvivor.pk).exists())

    # --- 4.3: SavedDish merge ---

    def test_saved_dish_merge(self):
        """user1 only saved dish_b → SavedDish reassigned.
        user2 saved both → duplicate SavedDish deleted."""
        saved_user1 = SavedDish.objects.create(dish=self.dish_b, user=self.user1)
        saved_user2_survivor = SavedDish.objects.create(dish=self.dish_a, user=self.user2)
        saved_user2_nonsurvivor = SavedDish.objects.create(dish=self.dish_b, user=self.user2)

        self._trigger_action([self.venue_a.pk, self.venue_b.pk])
        self._confirm_merge([self.venue_a.pk, self.venue_b.pk], self.venue_a.pk)

        # user1's saved dish reassigned to dish_a
        saved_user1.refresh_from_db()
        self.assertEqual(saved_user1.dish, self.dish_a)

        # user2's survivor saved dish preserved
        saved_user2_survivor.refresh_from_db()
        self.assertEqual(saved_user2_survivor.dish, self.dish_a)

        # user2's non-survivor saved dish deleted
        self.assertFalse(SavedDish.objects.filter(pk=saved_user2_nonsurvivor.pk).exists())

    # --- 4.4: cancel ---

    def test_cancel_aborts_merge(self):
        self._trigger_action([self.venue_a.pk, self.venue_b.pk])
        response = self.client.post(
            reverse("admin:catalog_venue_merge"),
            {"cancel": "Cancel", "selected_ids": [self.venue_a.pk, self.venue_b.pk]},
            follow=False,
        )
        self.assertRedirects(response, reverse("admin:catalog_venue_changelist"), fetch_redirect_response=False)
        self.assertEqual(Venue.objects.count(), 3)


# ──────────────────────────────────────────────────────────────────────────────
# VenueSuggestion tests
# ──────────────────────────────────────────────────────────────────────────────

from catalog.models import VenueSuggestion


class VenueSuggestionViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:suggest_venue")
        self.thanks_url = reverse("catalog:suggest_venue_thanks")

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_get_prefills_name_from_q(self):
        response = self.client.get(self.url + "?q=Casa+Bot%C3%ADn")
        self.assertContains(response, "Casa Bot\u00edn")

    def test_valid_post_creates_suggestion_and_redirects(self):
        response = self.client.post(
            self.url + "?q=Casa+Bot%C3%ADn",
            {"name": "Casa Bot\u00edn", "city": "Madrid"},
        )
        self.assertRedirects(response, self.thanks_url, fetch_redirect_response=False)
        suggestion = VenueSuggestion.objects.get()
        self.assertEqual(suggestion.name, "Casa Bot\u00edn")
        self.assertEqual(suggestion.city, "Madrid")
        self.assertEqual(suggestion.search_query, "Casa Bot\u00edn")
        self.assertEqual(suggestion.status, VenueSuggestion.STATUS_PENDING)

    def test_invalid_post_rerenders_form_with_errors(self):
        response = self.client.post(self.url, {"name": "", "city": ""})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("name", form.errors)
        self.assertIn("city", form.errors)
        self.assertEqual(VenueSuggestion.objects.count(), 0)

    def test_venue_list_shows_suggest_link_when_no_results_and_query(self):
        response = self.client.get(reverse("catalog:venue_list") + "?q=nonexistent")
        self.assertContains(response, "Suggest a venue")

    def test_venue_list_hides_suggest_link_when_no_query(self):
        response = self.client.get(reverse("catalog:venue_list"))
        self.assertNotContains(response, "Suggest a venue")


class VenueSuggestionAdminPromoteTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username="admin", password="pass", email="admin@example.com"
        )
        self.client.force_login(self.admin_user)
        self.suggestion = VenueSuggestion.objects.create(
            name="The Golden Fork",
            city="Lisbon",
            address="Rua do Ouro 10",
            website_url="https://goldenfork.pt",
        )

    def test_promote_to_new_venue_creates_venue_and_location(self):
        url = reverse("admin:catalog_venuesuggestion_changelist")
        response = self.client.post(
            url,
            {
                "action": "promote_to_new_venue_action",
                "_selected_action": [self.suggestion.pk],
            },
            follow=False,
        )
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, VenueSuggestion.STATUS_APPROVED)
        self.assertIsNotNone(self.suggestion.promoted_venue)
        venue = self.suggestion.promoted_venue
        self.assertEqual(venue.name, "The Golden Fork")
        self.assertEqual(venue.city, "Lisbon")
        self.assertFalse(venue.is_published)
        location = venue.locations.get()
        self.assertEqual(location.address, "Rua do Ouro 10")
        # Should redirect to Venue change page
        self.assertRedirects(
            response,
            reverse("admin:catalog_venue_change", args=[venue.pk]),
            fetch_redirect_response=False,
        )

    def test_promote_blocks_multi_selection(self):
        suggestion2 = VenueSuggestion.objects.create(name="Other", city="Porto")
        url = reverse("admin:catalog_venuesuggestion_changelist")
        self.client.post(
            url,
            {
                "action": "promote_to_new_venue_action",
                "_selected_action": [self.suggestion.pk, suggestion2.pk],
            },
        )
        self.assertEqual(Venue.objects.count(), 0)

    def test_promote_view_button(self):
        url = reverse("admin:catalog_venuesuggestion_promote", args=[self.suggestion.pk])
        response = self.client.get(url, follow=False)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, VenueSuggestion.STATUS_APPROVED)
        venue = self.suggestion.promoted_venue
        self.assertRedirects(
            response,
            reverse("admin:catalog_venue_change", args=[venue.pk]),
            fetch_redirect_response=False,
        )


class VenueSuggestionAdminAddLocationTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username="admin2", password="pass", email="admin2@example.com"
        )
        self.client.force_login(self.admin_user)
        self.existing_venue = Venue.objects.create(
            name="Taberna do Mar", slug="taberna-do-mar", city="Lisbon"
        )
        self.suggestion = VenueSuggestion.objects.create(
            name="Taberna do Mar",
            city="Porto",
            address="Rua da Alegria 5",
        )

    def test_add_location_form_renders(self):
        url = reverse("admin:catalog_venuesuggestion_add_location", args=[self.suggestion.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taberna do Mar")

    def test_add_location_post_creates_location_and_marks_approved(self):
        url = reverse("admin:catalog_venuesuggestion_add_location", args=[self.suggestion.pk])
        response = self.client.post(
            url,
            {"venue": self.existing_venue.pk},
            follow=False,
        )
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, VenueSuggestion.STATUS_APPROVED)
        self.assertEqual(self.suggestion.promoted_venue, self.existing_venue)
        location = self.existing_venue.locations.get()
        self.assertEqual(location.city, "Porto")
        self.assertEqual(location.address, "Rua da Alegria 5")
        self.assertRedirects(
            response,
            reverse("admin:catalog_venuelocation_change", args=[location.pk]),
            fetch_redirect_response=False,
        )


class VenueSuggestionRejectTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_superuser(
            username="admin_rej", password="pass", email="admin_rej@example.com"
        )
        self.client.force_login(self.admin_user)
        self.s1 = VenueSuggestion.objects.create(name="Café A", city="Porto")
        self.s2 = VenueSuggestion.objects.create(name="Café B", city="Lisbon")

    def _reject_url(self, *ids):
        id_str = ",".join(str(i) for i in ids)
        return reverse("admin:catalog_venuesuggestion_reject") + f"?ids={id_str}"

    def test_reject_confirmation_page_renders(self):
        response = self.client.get(self._reject_url(self.s1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Café A")

    def test_reject_single_sets_status_and_reason(self):
        response = self.client.post(
            self._reject_url(self.s1.pk),
            {"ids": str(self.s1.pk), "reason": "Venue already exists"},
        )
        self.assertRedirects(
            response,
            reverse("admin:catalog_venuesuggestion_changelist"),
            fetch_redirect_response=False,
        )
        self.s1.refresh_from_db()
        self.assertEqual(self.s1.status, VenueSuggestion.STATUS_REJECTED)
        self.assertEqual(self.s1.rejection_reason, "Venue already exists")

    def test_reject_bulk_updates_all_with_same_reason(self):
        self.client.post(
            self._reject_url(self.s1.pk, self.s2.pk),
            {"ids": f"{self.s1.pk},{self.s2.pk}", "reason": "Out of scope"},
        )
        self.s1.refresh_from_db()
        self.s2.refresh_from_db()
        self.assertEqual(self.s1.status, VenueSuggestion.STATUS_REJECTED)
        self.assertEqual(self.s2.status, VenueSuggestion.STATUS_REJECTED)
        self.assertEqual(self.s1.rejection_reason, "Out of scope")
        self.assertEqual(self.s2.rejection_reason, "Out of scope")

    def test_reject_blocked_if_any_suggestion_approved(self):
        self.s1.status = VenueSuggestion.STATUS_APPROVED
        self.s1.save()
        response = self.client.get(self._reject_url(self.s1.pk, self.s2.pk))
        self.assertRedirects(
            response,
            reverse("admin:catalog_venuesuggestion_changelist"),
            fetch_redirect_response=False,
        )
        self.s2.refresh_from_db()
        self.assertEqual(self.s2.status, VenueSuggestion.STATUS_PENDING)

    def test_reject_via_changelist_action_redirects_to_confirm(self):
        url = reverse("admin:catalog_venuesuggestion_changelist")
        response = self.client.post(
            url,
            {
                "action": "reject_suggestions",
                "_selected_action": [self.s1.pk],
            },
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("reject", response["Location"])
        self.assertIn(str(self.s1.pk), response["Location"])


class VenueSuggestionUserTrackingTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="alice", password="pass")
        self.suggest_url = reverse("catalog:suggest_venue")
        self.thanks_url = reverse("catalog:suggest_venue_thanks")
        self.profile_url = reverse("profile", kwargs={"username": "alice"})

    # 6.1 Authenticated submission
    def test_authenticated_submission_sets_submitted_by(self):
        self.client.force_login(self.user)
        response = self.client.post(self.suggest_url, {"name": "El Faro", "city": "Madrid"})
        self.assertRedirects(response, self.thanks_url, fetch_redirect_response=False)
        suggestion = VenueSuggestion.objects.get()
        self.assertEqual(suggestion.submitted_by, self.user)

    def test_authenticated_form_has_no_submitter_fields(self):
        self.client.force_login(self.user)
        response = self.client.get(self.suggest_url)
        form = response.context["form"]
        self.assertNotIn("submitter_name", form.fields)
        self.assertNotIn("submitter_email", form.fields)

    def test_authenticated_thanks_page_shows_profile_link(self):
        self.client.force_login(self.user)
        response = self.client.get(self.thanks_url)
        self.assertContains(response, "your profile")
        self.assertContains(response, reverse("profile", kwargs={"username": "alice"}))

    # 6.2 Anonymous submission
    def test_anonymous_submission_sets_no_submitted_by(self):
        self.client.post(self.suggest_url, {
            "name": "El Faro", "city": "Madrid",
            "submitter_name": "Bob", "submitter_email": "bob@example.com",
        })
        suggestion = VenueSuggestion.objects.get()
        self.assertIsNone(suggestion.submitted_by)
        self.assertEqual(suggestion.submitter_name, "Bob")

    def test_anonymous_form_has_submitter_fields(self):
        response = self.client.get(self.suggest_url)
        form = response.context["form"]
        self.assertIn("submitter_name", form.fields)
        self.assertIn("submitter_email", form.fields)

    def test_anonymous_thanks_page_no_profile_link(self):
        response = self.client.get(self.thanks_url)
        self.assertNotContains(response, "your profile")

    # 6.3 Profile section visibility
    def test_profile_section_visible_to_owner(self):
        VenueSuggestion.objects.create(name="El Faro", city="Madrid", submitted_by=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertContains(response, "Venue Suggestions")
        self.assertContains(response, "El Faro")

    def test_profile_section_hidden_from_other_user(self):
        from django.contrib.auth.models import User
        other = User.objects.create_user(username="bob2", password="pass")
        VenueSuggestion.objects.create(name="El Faro", city="Madrid", submitted_by=self.user)
        self.client.force_login(other)
        response = self.client.get(self.profile_url)
        self.assertNotContains(response, "Venue Suggestions")

    def test_profile_section_hidden_when_no_suggestions(self):
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertNotContains(response, "Venue Suggestions")

    # 6.4 Approved suggestion with venue link
    def test_approved_suggestion_shows_venue_link_when_published(self):
        venue = Venue.objects.create(name="El Faro", slug="el-faro", city="Madrid", is_published=True)
        VenueSuggestion.objects.create(
            name="El Faro", city="Madrid",
            submitted_by=self.user,
            status=VenueSuggestion.STATUS_APPROVED,
            promoted_venue=venue,
        )
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertContains(response, reverse("catalog:venue_detail", args=["el-faro"]))

    def test_approved_suggestion_hides_venue_link_when_unpublished(self):
        venue = Venue.objects.create(name="El Faro", slug="el-faro-2", city="Madrid", is_published=False)
        VenueSuggestion.objects.create(
            name="El Faro", city="Madrid",
            submitted_by=self.user,
            status=VenueSuggestion.STATUS_APPROVED,
            promoted_venue=venue,
        )
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertNotContains(response, reverse("catalog:venue_detail", args=["el-faro-2"]))

    # 6.5 Rejected suggestion shows reason
    def test_rejected_suggestion_shows_rejection_reason(self):
        VenueSuggestion.objects.create(
            name="Mesón del Jamón", city="Madrid",
            submitted_by=self.user,
            status=VenueSuggestion.STATUS_REJECTED,
            rejection_reason="Already in the catalog.",
        )
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertContains(response, "Already in the catalog.")


class CatalogTagsTests(SimpleTestCase):
    def test_price_level_known_enums(self):
        self.assertEqual(price_level_display("PRICE_LEVEL_FREE"), "Free")
        self.assertEqual(price_level_display("PRICE_LEVEL_INEXPENSIVE"), "€")
        self.assertEqual(price_level_display("PRICE_LEVEL_MODERATE"), "€€")
        self.assertEqual(price_level_display("PRICE_LEVEL_EXPENSIVE"), "€€€")
        self.assertEqual(price_level_display("PRICE_LEVEL_VERY_EXPENSIVE"), "€€€€")

    def test_price_level_unknown_and_blank_omitted(self):
        self.assertEqual(price_level_display(""), "")
        self.assertEqual(price_level_display(None), "")
        self.assertEqual(price_level_display("PRICE_LEVEL_UNKNOWN"), "")

    def test_operational_status_hidden(self):
        self.assertEqual(business_status_label("OPERATIONAL"), "")
        self.assertEqual(business_status_label(""), "")
        self.assertEqual(business_status_label(None), "")

    def test_closed_temporarily_labeled(self):
        self.assertEqual(business_status_label("CLOSED_TEMPORARILY"), "Closed temporarily")
        self.assertEqual(business_status_label("CLOSED_PERMANENTLY"), "Closed permanently")

    def test_generic_google_types_dropped(self):
        chips = public_place_types(
            ["restaurant", "food", "establishment", "point_of_interest", "cafe"],
            "restaurant",
        )
        self.assertEqual(chips, ["Cafe"])

    def test_humanize_primary_type(self):
        self.assertEqual(humanize_place_type("restaurant"), "Restaurant")
        self.assertEqual(humanize_place_type("hamburger_restaurant"), "Hamburger Restaurant")
        self.assertEqual(humanize_place_type(""), "")

    def test_missing_weekday_descriptions_yields_empty(self):
        self.assertEqual(weekday_hours(None), [])
        self.assertEqual(weekday_hours({"periods": []}), [])
        self.assertEqual(
            weekday_hours({"weekdayDescriptions": ["Monday: 12:00–23:00"]}),
            ["Monday: 12:00–23:00"],
        )

    def test_location_heading_omits_matching_venue_name(self):
        venue = type("Venue", (), {"name": "Café Santiago"})()
        matching = type("Loc", (), {"name": "Café Santiago"})()
        other = type("Loc", (), {"name": "Bonfim"})()
        self.assertEqual(location_heading(matching, venue), "")
        self.assertEqual(location_heading(other, venue), "Bonfim")

    def test_tel_href_keeps_digits(self):
        self.assertEqual(tel_href("222 055 797"), "tel:222055797")
        self.assertEqual(tel_href(""), "")


class VenueDetailDisplayTests(TestCase):
    def _url(self, slug):
        return reverse("catalog:venue_detail", kwargs={"slug": slug})

    def test_zero_locations_shows_city_without_locations_heading(self):
        Venue.objects.create(name="No Locs", slug="no-locs", city="Porto")
        response = self.client.get(self._url("no-locs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Locs")
        self.assertContains(response, "Porto")
        self.assertNotContains(response, "<h2>Locations</h2>")
        self.assertContains(response, "Dishes at No Locs")
        self.assertNotContains(response, "ChIJ")
        self.assertNotContains(response, "41.146945")

    def test_one_populated_location_is_flattened_into_hero(self):
        venue = Venue.objects.create(name="Café Santiago", slug="cafe-santiago", city="Porto")
        VenueLocation.objects.create(
            venue=venue,
            name="Café Santiago",
            city="Porto",
            address="Rua de Passos Manuel 226",
            postal_code="4000-382",
            neighbourhood="Bonfim",
            latitude=Decimal("41.146945"),
            longitude=Decimal("-8.605215"),
            google_place_id="ChIJsantiago",
            business_status="OPERATIONAL",
            phone="222 055 797",
            website_url="https://cafesantiago.pt/",
            google_maps_uri="https://maps.google.com/?cid=123",
            price_level="PRICE_LEVEL_MODERATE",
            primary_type="restaurant",
            types=["restaurant", "food", "cafe"],
            opening_hours={"weekdayDescriptions": ["Monday: 12:00–23:00"]},
            google_rating=Decimal("4.3"),
            google_user_rating_count=12000,
        )
        response = self.client.get(self._url("cafe-santiago"))
        html = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Café Santiago</h1>", html=True)
        self.assertNotContains(response, "<h2>Locations</h2>")
        self.assertNotContains(response, 'class="location-branch-name"')
        self.assertContains(response, "Bonfim")
        self.assertContains(response, "Porto")
        self.assertContains(response, "Rua de Passos Manuel 226")
        self.assertContains(response, "4000-382")
        self.assertContains(response, 'href="tel:222055797"')
        self.assertContains(response, "222 055 797")
        self.assertContains(response, 'href="https://cafesantiago.pt/"')
        self.assertContains(response, 'href="https://maps.google.com/?cid=123"')
        self.assertContains(response, "Get Directions")
        self.assertContains(response, "Open in Google Maps")
        self.assertContains(response, "€€")
        self.assertNotContains(response, "PRICE_LEVEL_MODERATE")
        self.assertContains(response, "Restaurant")
        self.assertContains(response, "Cafe")
        self.assertContains(response, "Monday: 12:00–23:00")
        self.assertContains(response, "Google")
        self.assertContains(response, "4.3")
        self.assertContains(response, "12000")
        self.assertContains(response, '<p class="location-google-rating">')
        rating_html = html.split('<p class="location-google-rating">', 1)[1].split("</p>", 1)[0]
        self.assertIn("4.3", rating_html)
        self.assertIn("Google", rating_html)
        self.assertNotIn("★", rating_html)
        self.assertNotContains(response, "Operational")
        self.assertNotContains(response, "ChIJsantiago")
        self.assertNotIn('class="venue-locations"', html)
        hero, dishes = html.split("Dishes at Café Santiago", 1)
        self.assertIn("Rua de Passos Manuel 226", hero)
        self.assertIn("location-facts", hero)
        self.assertNotIn("location-facts", dishes)
        location = VenueLocation.objects.get(venue=venue)
        self.assertNotContains(response, location.get_absolute_url())

    def test_one_sparse_location_omits_blank_fields(self):
        venue = Venue.objects.create(name="Sparse Spot", slug="sparse-spot", city="Porto")
        VenueLocation.objects.create(
            venue=venue,
            city="Porto",
            address="Rua Nova 1",
        )
        response = self.client.get(self._url("sparse-spot"))
        self.assertContains(response, "Porto")
        self.assertContains(response, "Rua Nova 1")
        self.assertNotContains(response, "<h2>Locations</h2>")
        self.assertNotContains(response, "Hours")
        self.assertNotContains(response, "Website")
        self.assertNotContains(response, "Google")
        self.assertNotContains(response, "€")
        self.assertNotContains(response, "tel:")
        self.assertNotContains(response, "Get Directions")
        self.assertNotContains(response, "Open in Google Maps")

    def test_two_locations_use_locations_segment(self):
        venue = Venue.objects.create(name="Prego House", slug="prego-house", city="Porto")
        loc_a = VenueLocation.objects.create(
            venue=venue,
            name="Bonfim",
            city="Porto",
            address="Rua A 1",
            phone="222 000 001",
            opening_hours={"weekdayDescriptions": ["Monday: 12:00–23:00"]},
            google_rating=Decimal("4.1"),
            google_user_rating_count=10,
        )
        loc_b = VenueLocation.objects.create(
            venue=venue,
            name="Foz",
            city="Porto",
            address="Rua B 2",
            phone="222 000 002",
            opening_hours={"weekdayDescriptions": ["Tuesday: 11:00–22:00"]},
            google_rating=Decimal("4.8"),
            google_user_rating_count=20,
        )
        dish_type = DishType.objects.create(name="Prego", slug="prego")
        Dish.objects.create(
            name="Prego no Pão",
            slug="prego-no-pao",
            dish_type=dish_type,
            venue=venue,
        )
        response = self.client.get(self._url("prego-house"))
        html = response.content.decode()
        self.assertContains(response, "<h2>Locations</h2>")
        self.assertContains(response, "2 locations")
        self.assertContains(response, "Porto")
        self.assertContains(response, "Bonfim")
        self.assertContains(response, "Foz")
        self.assertContains(response, "Rua A 1")
        self.assertContains(response, "Rua B 2")
        self.assertContains(response, loc_a.get_absolute_url())
        self.assertContains(response, loc_b.get_absolute_url())
        self.assertNotContains(response, "Monday: 12:00–23:00")
        self.assertNotContains(response, "Tuesday: 11:00–22:00")
        self.assertNotContains(response, "222 000 001")
        self.assertNotContains(response, "222 000 002")
        self.assertNotContains(response, "Hours")
        self.assertNotContains(response, "tel:")
        self.assertNotContains(response, "4.1")
        self.assertNotContains(response, "4.8")
        self.assertContains(response, "Prego no Pão")
        self.assertContains(response, "Dishes at Prego House")
        locations_at = html.index("<h2>Locations</h2>")
        dishes_at = html.index("Dishes at Prego House")
        self.assertLess(locations_at, dishes_at)
        hero = html[:locations_at]
        self.assertNotIn("Rua A 1", hero)
        self.assertNotIn("Rua B 2", hero)
        self.assertIn("2 locations", hero)

    def test_closed_temporarily_shows_warning(self):
        venue = Venue.objects.create(name="Shut Café", slug="shut-cafe", city="Porto")
        VenueLocation.objects.create(
            venue=venue,
            city="Porto",
            business_status="CLOSED_TEMPORARILY",
        )
        response = self.client.get(self._url("shut-cafe"))
        self.assertContains(response, "Closed temporarily")
        self.assertContains(response, "venue-chip--warning")


class VenueLocationDetailTests(TestCase):
    def _url(self, slug, pk):
        return reverse("catalog:venue_location_detail", kwargs={"slug": slug, "pk": pk})

    def _chain_venue(self):
        venue = Venue.objects.create(name="Prego House", slug="prego-house", city="Porto")
        loc_a = VenueLocation.objects.create(
            venue=venue,
            name="Bonfim",
            city="Porto",
            address="Rua A 1",
            postal_code="4000-001",
            neighbourhood="Bonfim",
            latitude=Decimal("41.146945"),
            longitude=Decimal("-8.605215"),
            google_place_id="ChIJBonfim",
            business_status="OPERATIONAL",
            phone="222 000 001",
            website_url="https://pregohouse.pt/bonfim",
            google_maps_uri="https://maps.google.com/?cid=111",
            price_level="PRICE_LEVEL_MODERATE",
            primary_type="restaurant",
            types=["restaurant", "food", "cafe"],
            opening_hours={"weekdayDescriptions": ["Monday: 12:00–23:00"]},
            google_rating=Decimal("4.1"),
            google_user_rating_count=10,
        )
        VenueLocation.objects.create(
            venue=venue,
            name="Foz",
            city="Porto",
            address="Rua B 2",
        )
        return venue, loc_a

    def test_populated_location_shows_facts_without_dishes(self):
        venue, loc_a = self._chain_venue()
        dish_type = DishType.objects.create(name="Prego", slug="prego")
        Dish.objects.create(
            name="Prego no Pão",
            slug="prego-no-pao",
            dish_type=dish_type,
            venue=venue,
        )
        response = self.client.get(self._url(venue.slug, loc_a.pk))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Bonfim</h1>", html=True)
        self.assertContains(
            response,
            reverse("catalog:venue_detail", kwargs={"slug": venue.slug}),
        )
        self.assertContains(response, "Prego House")
        self.assertContains(response, "Rua A 1")
        self.assertContains(response, "4000-001")
        self.assertContains(response, "Bonfim")
        self.assertContains(response, 'href="tel:222000001"')
        self.assertContains(response, "222 000 001")
        self.assertContains(response, 'href="https://pregohouse.pt/bonfim"')
        self.assertContains(response, 'href="https://maps.google.com/?cid=111"')
        self.assertContains(response, "Get Directions")
        self.assertContains(response, "Open in Google Maps")
        self.assertContains(response, "€€")
        self.assertContains(response, "Restaurant")
        self.assertContains(response, "Cafe")
        self.assertContains(response, "Monday: 12:00–23:00")
        self.assertContains(response, "Google")
        self.assertContains(response, "4.1")
        self.assertNotContains(response, "Dishes at Prego House")
        self.assertNotContains(response, "Prego no Pão")
        self.assertNotContains(response, "ChIJBonfim")
        self.assertNotContains(response, "Operational")

    def test_sparse_location_omits_blank_fields(self):
        venue = Venue.objects.create(name="Chain Café", slug="chain-cafe", city="Porto")
        sparse = VenueLocation.objects.create(
            venue=venue, name="Campanhã", city="Porto", address="Rua Nova 1"
        )
        VenueLocation.objects.create(
            venue=venue, name="Cedofeita", city="Porto", address="Rua Velha 2"
        )
        response = self.client.get(self._url(venue.slug, sparse.pk))
        self.assertContains(response, "Porto")
        self.assertContains(response, "Rua Nova 1")
        self.assertNotContains(response, "Hours")
        self.assertNotContains(response, "Website")
        self.assertNotContains(response, "Google")
        self.assertNotContains(response, "€")
        self.assertNotContains(response, "tel:")
        self.assertNotContains(response, "Get Directions")
        self.assertNotContains(response, "Open in Google Maps")

    def test_one_location_url_redirects_to_venue(self):
        venue = Venue.objects.create(name="Café Santiago", slug="cafe-santiago", city="Porto")
        location = VenueLocation.objects.create(
            venue=venue, city="Porto", address="Rua de Passos Manuel 226"
        )
        response = self.client.get(self._url(venue.slug, location.pk))
        self.assertRedirects(
            response,
            reverse("catalog:venue_detail", kwargs={"slug": venue.slug}),
        )

    def test_unpublished_parent_is_not_found(self):
        venue = Venue.objects.create(
            name="Hidden Chain", slug="hidden-chain", city="Porto", is_published=False
        )
        loc_a = VenueLocation.objects.create(venue=venue, name="A", city="Porto")
        VenueLocation.objects.create(venue=venue, name="B", city="Porto")
        response = self.client.get(self._url(venue.slug, loc_a.pk))
        self.assertEqual(response.status_code, 404)

    def test_slug_mismatch_is_not_found(self):
        venue, loc_a = self._chain_venue()
        other = Venue.objects.create(name="Other", slug="other-venue", city="Lisboa")
        response = self.client.get(self._url(other.slug, loc_a.pk))
        self.assertEqual(response.status_code, 404)

    def test_missing_location_is_not_found(self):
        venue, _loc_a = self._chain_venue()
        response = self.client.get(self._url(venue.slug, 99999))
        self.assertEqual(response.status_code, 404)
