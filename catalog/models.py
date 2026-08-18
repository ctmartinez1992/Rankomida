from django.conf import settings
from django.db import models


class DishType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='dish_types/photos/', null=True, blank=True)
    photo_credit = models.CharField(max_length=255, blank=True)
    photo_source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Venue(models.Model):
    SOURCE_MANUAL = "manual"
    SOURCE_GOOGLE = "google"
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_GOOGLE, "Google Places"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    city = models.CharField(max_length=120)
    is_published = models.BooleanField(default=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    photo = models.ImageField(upload_to='venues/photos/', null=True, blank=True)
    photo_credit = models.CharField(max_length=255, blank=True)
    photo_source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class VenueLocation(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_place_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    business_status = models.CharField(max_length=32, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    neighbourhood = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website_url = models.URLField(max_length=500, blank=True)
    google_maps_uri = models.URLField(max_length=500, blank=True)
    price_level = models.CharField(max_length=32, blank=True)
    primary_type = models.CharField(max_length=80, blank=True)
    types = models.JSONField(default=list, blank=True)
    opening_hours = models.JSONField(null=True, blank=True)
    google_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    google_user_rating_count = models.PositiveIntegerField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "city"]

    def __str__(self) -> str:
        label = self.name or self.city
        return f"{self.venue.name} — {label}"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse(
            "catalog:venue_location_detail",
            kwargs={"slug": self.venue.slug, "pk": self.pk},
        )


class Dish(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    dish_type = models.ForeignKey(
        DishType,
        on_delete=models.PROTECT,
        related_name="dishes",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="dishes",
    )
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='dishes/photos/', null=True, blank=True)
    photo_credit = models.CharField(max_length=255, blank=True)
    photo_source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "venue")

    def __str__(self) -> str:
        return f"{self.name} ({self.venue.name})"


class SavedDish(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_dishes",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-saved_at"]
        unique_together = ("user", "dish")

    def __str__(self) -> str:
        return f"{self.user} saved {self.dish}"


class VenueSuggestion(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_DUPLICATE = "duplicate"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_DUPLICATE, "Duplicate"),
    ]

    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    submitter_name = models.CharField(max_length=120, blank=True)
    submitter_email = models.EmailField(blank=True)
    search_query = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="venue_suggestions",
    )
    rejection_reason = models.TextField(blank=True)
    promoted_venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suggested_from",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.city})"
