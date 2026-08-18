## 1. Formatters

- [x] 1.1 Create `catalog/templatetags/catalog_tags.py` (with `__init__.py` if needed) exposing filters/tags for price level (€/€€/€€€/€€€€/Free), non-OPERATIONAL business status label, humanized primary type, filtered type chips, and `weekdayDescriptions` from `opening_hours`
- [x] 1.2 Unit-test the formatters: known price enums, unknown/blank omitted, OPERATIONAL hidden, CLOSED_TEMPORARILY labeled, generic Google types dropped, missing `weekdayDescriptions` yields empty

## 2. View

- [x] 2.1 Prefetch `locations` on `VenueDetailView.get_queryset` so the template can branch on location count without extra queries

## 3. CSS

- [x] 3.1 Add venue-detail styles in `templates/base.html`: full-container venue page wrapper (do not widen `.detail-card`), location fact list, warning chip, action links, type chips. Reuse existing `--color-*` tokens and `.card` / `.card-grid` for location cards

## 4. Templates

- [x] 4.1 Create `templates/catalog/_venue_location_facts.html` that renders one location's public facts, omitting blanks, using the formatters and maps/phone/website links
- [x] 4.2 Rebuild `templates/catalog/venue_detail.html`: 0 locations → hero with name/photo/`venue.city`; 1 location → flatten facts into the hero with no Locations heading; 2+ → venue-level hero plus a Locations segment of cards; Dishes section unchanged and last

## 5. Tests

- [x] 5.1 Test zero locations: city shown, no Locations heading, internal fields (place id, raw coords) absent
- [x] 5.2 Test one fully populated location: facts inlined in the hero, no Locations heading, phone `tel:` link, Google rating labeled numerically (not Rankomida stars), matching branch name not repeated
- [x] 5.3 Test one sparse location: blank phone/hours/price omitted
- [x] 5.4 Test two-plus locations: Locations heading, one card per location, hero shows home city and location count, Dishes still listed after Locations
