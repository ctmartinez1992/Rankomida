from django.contrib import admin

from .models import Dish, DishType, Venue


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "slug")
    search_fields = ("name", "city", "slug")


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_type", "venue", "is_published")
    list_filter = ("dish_type", "is_published")
    search_fields = ("name", "venue__name")
