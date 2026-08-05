from django.contrib import admin

from .models import Dish, DishType, Venue, VenueLocation


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    fields = ("name", "slug", "description", "is_active", "photo")


class VenueLocationInline(admin.StackedInline):
    model = VenueLocation
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "slug")
    search_fields = ("name", "city", "slug")
    fields = ("name", "slug", "city", "photo")
    inlines = [VenueLocationInline]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_type", "venue", "is_published")
    list_filter = ("dish_type", "is_published")
    search_fields = ("name", "venue__name")
    fields = ("name", "slug", "dish_type", "venue", "description", "is_published", "photo")
