from django.contrib import admin
from django.utils.translation import ngettext

from .models import Dish, DishType, SavedDish, Venue, VenueLocation


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    fields = ("name", "slug", "description", "is_active", "photo", "photo_credit", "photo_source_url", "created_at", "updated_at")


class VenueLocationInline(admin.StackedInline):
    model = VenueLocation
    extra = 1
    readonly_fields = ("google_place_id", "last_synced_at", "created_at", "updated_at")
    fields = (
        "name",
        "city",
        "address",
        "latitude",
        "longitude",
        "postal_code",
        "neighbourhood",
        "phone",
        "website_url",
        "google_maps_uri",
        "business_status",
        "price_level",
        "primary_type",
        "types",
        "opening_hours",
        "google_rating",
        "google_user_rating_count",
        "google_place_id",
        "last_synced_at",
        "created_at",
        "updated_at",
    )


@admin.action(description="Publish selected venues")
def publish_venues(modeladmin, request, queryset):
    updated = queryset.update(is_published=True)
    modeladmin.message_user(
        request,
        ngettext(
            "%(count)d venue was published.",
            "%(count)d venues were published.",
            updated,
        ) % {"count": updated},
    )


@admin.action(description="Unpublish selected venues")
def unpublish_venues(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(
        request,
        ngettext(
            "%(count)d venue was unpublished.",
            "%(count)d venues were unpublished.",
            updated,
        ) % {"count": updated},
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "slug", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "source", "city")
    search_fields = ("name", "city", "slug")
    actions = [publish_venues, unpublish_venues]
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "name",
        "slug",
        "city",
        "is_published",
        "source",
        "photo",
        "photo_credit",
        "photo_source_url",
    )
    inlines = [VenueLocationInline]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_type", "venue", "is_published")
    list_filter = ("dish_type", "is_published")
    search_fields = ("name", "venue__name")
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "name",
        "slug",
        "dish_type",
        "venue",
        "description",
        "is_published",
        "photo",
        "photo_credit",
        "photo_source_url",
        "created_at",
        "updated_at",
    )


@admin.register(SavedDish)
class SavedDishAdmin(admin.ModelAdmin):
    list_display = ("user", "dish", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("user__username", "dish__name", "dish__slug")
    autocomplete_fields = ("user", "dish")
    readonly_fields = ("saved_at", "updated_at")
