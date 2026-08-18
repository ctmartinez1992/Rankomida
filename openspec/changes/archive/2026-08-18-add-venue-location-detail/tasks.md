## 1. URL and view

- [x] 1.1 Add `VenueLocation.get_absolute_url()` reversing `catalog:venue_location_detail` with venue slug and pk
- [x] 1.2 Add `/venues/<slug>/locations/<pk>/` named `venue_location_detail` in `catalog/urls.py`
- [x] 1.3 Add `VenueLocationDetailView`: lookup by pk + `venue__slug` + `venue__is_published=True` (404 on miss/mismatch/unpublished); redirect to venue detail when the venue has fewer than 2 locations; `select_related("venue")`

## 2. Templates

- [x] 2.1 Add a compact location teaser (heading, neighbourhood/city, address, non-OPERATIONAL warning, link to detail) used by 2+ cards on `venue_detail.html`; stop including the full facts partial in those cards
- [x] 2.2 Create `templates/catalog/venue_location_detail.html`: `.detail-card`, breadcrumb All Venues → venue → heading, H1 + venue subtitle link, include `_venue_location_facts.html`, no photo, no dishes
- [x] 2.3 Add card/link CSS in `templates/base.html` if the teaser needs it; reuse existing tokens
- [x] 2.4 Link location names from `dish_detail.html` compact list and `_community_notes.html` via `get_absolute_url`; prefetch `venue__locations` on `DishDetailView` if needed

## 3. Tests

- [x] 3.1 Keep 0/1 venue-detail tests; assert one-location venue page does not link the location URL
- [x] 3.2 Update 2+ venue-detail tests: Locations heading, compact teasers with addresses and detail links, hours/phone/Google rating absent from the venue page, Dishes still after Locations
- [x] 3.3 Test location detail for a 2+ venue: full public facts, parent venue link, no Dishes listing, internal fields omitted
- [x] 3.4 Test 1-location location URL redirects to venue detail; unpublished parent, slug mismatch, and missing pk return 404
