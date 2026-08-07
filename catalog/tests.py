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
