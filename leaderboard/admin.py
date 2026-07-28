from django.contrib import admin

from .models import DishAggregateScore


@admin.register(DishAggregateScore)
class DishAggregateScoreAdmin(admin.ModelAdmin):
    list_display = ("dish", "composite_score", "rating_count", "updated_at")
    list_filter = ("dish__dish_type",)
    search_fields = ("dish__name", "dish__venue__name")
