from django.contrib import admin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import ngettext

from .models import Dish, DishType, SavedDish, Venue, VenueLocation, VenueSuggestion


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


def _perform_merge(survivor, venues_to_delete, new_name=None):
    """Merge venues_to_delete into survivor atomically."""
    # Stamp survivor's own locations with the survivor name if they have no name yet.
    survivor.locations.filter(name="").update(name=survivor.name)

    survivor_dish_names = {d.name: d for d in survivor.dishes.all()}

    for venue in venues_to_delete:
        # 1. Stamp each location with the venue's name, then reassign to survivor.
        for location in venue.locations.all():
            if not location.name:
                location.name = venue.name
            location.venue = survivor
            location.save(update_fields=["name", "venue"])

        # 2. Handle dishes
        for dish in list(venue.dishes.all()):
            if dish.name not in survivor_dish_names:
                dish.venue = survivor
                dish.save()
                survivor_dish_names[dish.name] = dish
            else:
                survivor_dish = survivor_dish_names[dish.name]

                # Merge RatingSubmissions
                existing_user_ids = set(
                    survivor_dish.rating_submissions.values_list("user_id", flat=True)
                )
                for submission in list(dish.rating_submissions.all()):
                    if submission.user_id in existing_user_ids:
                        submission.delete()
                    else:
                        submission.dish = survivor_dish
                        submission.save()
                        existing_user_ids.add(submission.user_id)

                # Merge SavedDishes
                saved_user_ids = set(
                    survivor_dish.saved_by.values_list("user_id", flat=True)
                )
                for saved in list(dish.saved_by.all()):
                    if saved.user_id in saved_user_ids:
                        saved.delete()
                    else:
                        saved.dish = survivor_dish
                        saved.save()
                        saved_user_ids.add(saved.user_id)

                dish.delete()

        venue.delete()

    if new_name:
        survivor.name = new_name
        survivor.save(update_fields=["name"])


@admin.action(description="Merge selected venues into one")
def merge_venues(modeladmin, request, queryset):
    if queryset.count() < 2:
        modeladmin.message_user(
            request,
            "Select at least 2 venues to merge.",
            level="error",
        )
        return
    selected_ids = list(queryset.values_list("pk", flat=True))
    request.session["merge_venue_ids"] = selected_ids
    merge_url = reverse("admin:catalog_venue_merge")
    return HttpResponseRedirect(merge_url)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "slug", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "source", "city")
    search_fields = ("name", "city", "slug")
    list_per_page = 1000
    actions = [publish_venues, unpublish_venues, merge_venues]
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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("merge/", self.admin_site.admin_view(self.merge_view), name="catalog_venue_merge"),
        ]
        return custom + urls

    def merge_view(self, request):
        if request.method == "POST" and "cancel" in request.POST:
            return HttpResponseRedirect(reverse("admin:catalog_venue_changelist"))

        if request.method == "POST":
            selected_ids = [int(i) for i in request.POST.getlist("selected_ids")]
            survivor_id = int(request.POST.get("survivor_id"))
            venues_to_delete = list(Venue.objects.filter(pk__in=selected_ids).exclude(pk=survivor_id))
            survivor = Venue.objects.get(pk=survivor_id)
            new_name = request.POST.get("new_name", "").strip() or None
            with transaction.atomic():
                _perform_merge(survivor, venues_to_delete, new_name=new_name)
            count = len(venues_to_delete)
            self.message_user(
                request,
                ngettext(
                    'Merged %(count)d venue into \u201c%(survivor)s\u201d.',
                    'Merged %(count)d venues into \u201c%(survivor)s\u201d.',
                    count,
                ) % {"count": count, "survivor": survivor.name},
            )
            return HttpResponseRedirect(reverse("admin:catalog_venue_changelist"))

        # GET: build confirmation context
        selected_ids = request.session.get("merge_venue_ids", [])
        venues = list(Venue.objects.filter(pk__in=selected_ids).prefetch_related("locations", "dishes"))

        # Compute conflict summary: dishes whose name appears in 2+ venues
        name_to_venues = {}
        for venue in venues:
            for dish in venue.dishes.all():
                name_to_venues.setdefault(dish.name, []).append(venue.name)
        conflicts = [name for name, vns in name_to_venues.items() if len(vns) > 1]

        venue_summaries = [
            {
                "venue": v,
                "location_count": v.locations.count(),
                "dish_count": v.dishes.count(),
            }
            for v in venues
        ]

        context = {
            **self.admin_site.each_context(request),
            "title": "Merge Venues",
            "venue_summaries": venue_summaries,
            "selected_ids": selected_ids,
            "conflicts": conflicts,
            "total_locations": sum(s["location_count"] for s in venue_summaries),
            "total_dishes": sum(s["dish_count"] for s in venue_summaries),
        }
        return render(request, "admin/catalog/venue/merge_confirmation.html", context)


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


@admin.register(VenueLocation)
class VenueLocationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "venue", "city", "address")
    list_filter = ("city",)
    search_fields = ("venue__name", "city", "address")
    readonly_fields = ("google_place_id", "last_synced_at", "created_at", "updated_at")
    raw_id_fields = ("venue",)


@admin.register(SavedDish)
class SavedDishAdmin(admin.ModelAdmin):
    list_display = ("user", "dish", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("user__username", "dish__name", "dish__slug")
    autocomplete_fields = ("user", "dish")
    readonly_fields = ("saved_at", "updated_at")


def _promote_suggestion_to_venue(suggestion):
    """Create Venue + VenueLocation from a suggestion. Returns the new Venue."""
    from django.utils.text import slugify
    base_slug = slugify(suggestion.name)
    slug = base_slug
    counter = 1
    while Venue.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    with transaction.atomic():
        venue = Venue.objects.create(
            name=suggestion.name,
            slug=slug,
            city=suggestion.city,
            source=Venue.SOURCE_MANUAL,
            is_published=False,
        )
        VenueLocation.objects.create(
            venue=venue,
            city=suggestion.city,
            address=suggestion.address,
            website_url=suggestion.website_url,
        )
        suggestion.status = VenueSuggestion.STATUS_APPROVED
        suggestion.promoted_venue = venue
        suggestion.save(update_fields=["status", "promoted_venue", "updated_at"])

    return venue


@admin.action(description="Promote to new Venue")
def promote_to_new_venue_action(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Select exactly one suggestion to promote.",
            level="error",
        )
        return
    suggestion = queryset.first()
    venue = _promote_suggestion_to_venue(suggestion)
    modeladmin.message_user(
        request,
        f'Suggestion promoted: Venue "{venue.name}" created (unpublished).',
    )
    return HttpResponseRedirect(
        reverse("admin:catalog_venue_change", args=[venue.pk])
    )


@admin.register(VenueSuggestion)
class VenueSuggestionAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "submitted_by", "status", "search_query", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "city", "submitter_email")
    readonly_fields = ("search_query", "submitted_by", "promoted_venue_link", "created_at", "updated_at")
    ordering = ("-created_at",)
    actions = [promote_to_new_venue_action, "reject_suggestions"]

    fieldsets = (
        (None, {
            "fields": ("name", "city", "address", "website_url", "notes", "status"),
        }),
        ("Submitter", {
            "fields": ("submitted_by", "submitter_name", "submitter_email"),
            "classes": ("collapse",),
        }),
        ("Context", {
            "fields": ("search_query", "promoted_venue_link", "rejection_reason", "created_at", "updated_at"),
        }),
    )

    def promoted_venue_link(self, obj):
        if obj.promoted_venue_id:
            url = reverse("admin:catalog_venue_change", args=[obj.promoted_venue_id])
            return format_html('<a href="{}">{}</a>', url, obj.promoted_venue)
        return "—"
    promoted_venue_link.short_description = "Promoted venue"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/promote/",
                self.admin_site.admin_view(self.promote_view),
                name="catalog_venuesuggestion_promote",
            ),
            path(
                "<int:pk>/add-location/",
                self.admin_site.admin_view(self.add_location_view),
                name="catalog_venuesuggestion_add_location",
            ),
            path(
                "reject/",
                self.admin_site.admin_view(self.reject_view),
                name="catalog_venuesuggestion_reject",
            ),
        ]
        return custom + urls

    def promote_view(self, request, pk):
        from django.shortcuts import get_object_or_404
        suggestion = get_object_or_404(VenueSuggestion, pk=pk)
        venue = _promote_suggestion_to_venue(suggestion)
        self.message_user(
            request,
            f'Suggestion promoted: Venue "{venue.name}" created (unpublished).',
        )
        return HttpResponseRedirect(
            reverse("admin:catalog_venue_change", args=[venue.pk])
        )

    def add_location_view(self, request, pk):
        from django import forms as django_forms
        from django.shortcuts import get_object_or_404

        suggestion = get_object_or_404(VenueSuggestion, pk=pk)

        class VenueSelectForm(django_forms.Form):
            venue = django_forms.ModelChoiceField(
                queryset=Venue.objects.order_by("name"),
                label="Existing venue",
                help_text="The location will be added to this venue.",
            )

        if request.method == "POST":
            if "cancel" in request.POST:
                return HttpResponseRedirect(
                    reverse("admin:catalog_venuesuggestion_change", args=[pk])
                )
            form = VenueSelectForm(request.POST)
            if form.is_valid():
                selected_venue = form.cleaned_data["venue"]
                with transaction.atomic():
                    location = VenueLocation.objects.create(
                        venue=selected_venue,
                        city=suggestion.city,
                        address=suggestion.address,
                        website_url=suggestion.website_url,
                    )
                    suggestion.status = VenueSuggestion.STATUS_APPROVED
                    suggestion.promoted_venue = selected_venue
                    suggestion.save(update_fields=["status", "promoted_venue", "updated_at"])
                self.message_user(
                    request,
                    f'New location added to "{selected_venue.name}".',
                )
                return HttpResponseRedirect(
                    reverse("admin:catalog_venuelocation_change", args=[location.pk])
                )
        else:
            form = VenueSelectForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Add as location of existing venue",
            "suggestion": suggestion,
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/catalog/venuesuggestion/add_location.html", context)

    def reject_view(self, request, pk=None):
        from django import forms as django_forms
        from django.utils.html import escape

        raw_ids = request.POST.get("ids") or request.GET.get("ids", "")
        try:
            ids = [int(i) for i in raw_ids.split(",") if i.strip()]
        except ValueError:
            ids = []

        suggestions = list(VenueSuggestion.objects.filter(pk__in=ids))

        # Guard: block if any suggestion is already approved
        approved = [s for s in suggestions if s.status == VenueSuggestion.STATUS_APPROVED]
        if approved:
            names = ", ".join(f'"{s.name}"' for s in approved)
            self.message_user(
                request,
                f"Cannot reject already-approved suggestion(s): {names}.",
                level="error",
            )
            return HttpResponseRedirect(reverse("admin:catalog_venuesuggestion_changelist"))

        class RejectionForm(django_forms.Form):
            reason = django_forms.CharField(
                label="Reason",
                required=False,
                widget=django_forms.Textarea(attrs={"rows": 3}),
                help_text="Optional. Applies to all selected suggestions.",
            )
            ids = django_forms.CharField(widget=django_forms.HiddenInput)

        if request.method == "POST":
            if "cancel" in request.POST:
                return HttpResponseRedirect(reverse("admin:catalog_venuesuggestion_changelist"))
            form = RejectionForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data["reason"]
                count = len(suggestions)
                VenueSuggestion.objects.filter(pk__in=ids).update(
                    status=VenueSuggestion.STATUS_REJECTED,
                    rejection_reason=reason,
                )
                self.message_user(
                    request,
                    ngettext(
                        "%(count)d suggestion rejected.",
                        "%(count)d suggestions rejected.",
                        count,
                    ) % {"count": count},
                )
                return HttpResponseRedirect(reverse("admin:catalog_venuesuggestion_changelist"))
        else:
            form = RejectionForm(initial={"ids": raw_ids})

        context = {
            **self.admin_site.each_context(request),
            "title": "Reject suggestion(s)",
            "suggestions": suggestions,
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/catalog/venuesuggestion/reject_confirmation.html", context)

    @admin.action(description="Reject suggestion(s)")
    def reject_suggestions(self, request, queryset):
        ids = ",".join(str(pk) for pk in queryset.values_list("pk", flat=True))
        return HttpResponseRedirect(
            reverse("admin:catalog_venuesuggestion_reject") + f"?ids={ids}"
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["promote_url"] = reverse(
            "admin:catalog_venuesuggestion_promote", args=[object_id]
        )
        extra_context["add_location_url"] = reverse(
            "admin:catalog_venuesuggestion_add_location", args=[object_id]
        )
        extra_context["reject_url"] = (
            reverse("admin:catalog_venuesuggestion_reject") + f"?ids={object_id}"
        )
        return super().change_view(request, object_id, form_url, extra_context)
