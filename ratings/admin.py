from django.contrib import admin

from .models import CriteriaTemplate, RatingCriterionScore, RatingSubmission


class RatingCriterionScoreInline(admin.TabularInline):
    model = RatingCriterionScore
    extra = 0


@admin.register(CriteriaTemplate)
class CriteriaTemplateAdmin(admin.ModelAdmin):
    list_display = ("dish_type", "label", "key", "weight", "is_required", "is_active")
    list_filter = ("dish_type", "is_required", "is_active")
    search_fields = ("label", "key", "dish_type__name")


@admin.register(RatingSubmission)
class RatingSubmissionAdmin(admin.ModelAdmin):
    list_display = ("dish", "user", "overall_score", "created_at")
    list_filter = ("dish__dish_type",)
    search_fields = ("dish__name", "user__username")
    inlines = [RatingCriterionScoreInline]
