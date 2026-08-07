# Spec: Profile DishType Filter

## Behaviour

- The profile ratings fragment accepts an optional `dish_type` query param (a DishType slug).
- When `dish_type` is absent or empty, all of the user's ratings are shown (existing behaviour preserved).
- When `dish_type` matches a known slug, only ratings for dishes of that type are shown.
- When `dish_type` does not match any known slug, it is silently ignored and all ratings are shown.
- The filter only shows DishTypes for which **the viewed user has at least one rating**, and which are `is_active=True`.
- The filter list is ordered alphabetically by name.
- An "All" option is always present and active by default (when no dish_type is selected).
- The selected `dish_type` is preserved when the user changes sort order, and vice versa.
- The selected `dish_type` is reset to page 1 when clicked.
- The filter is hidden (not rendered) when the user has ratings for only one DishType (no meaningful filtering possible).

## Access Rules

- The filter is visible on both public and own profiles (wherever the ratings fragment is shown).
- Private profiles continue to block access as before; the filter does not change this.

## Edge Cases

- A user with 0 ratings sees no filter bar and the existing "No ratings yet." message.
- A user with ratings in only 1 DishType sees no filter bar (single type = no useful filter).
