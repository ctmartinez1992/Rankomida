# Tasks: Profile DishType Filter

## Task List

- [x] **T1: Extend ProfileRatingsFragmentView with dish_type filtering**
  - In `accounts/views.py`, read `dish_type` from `request.GET`.
  - Filter `qs` by `dish__dish_type__slug=dish_type_slug` when the param is present and non-empty.
  - If the slug doesn't match any DishType with `is_active=True`, fall back to no filter.
  - Build a `dish_types` queryset of DishTypes the user has rated (distinct, is_active, ordered by name).
  - Pass `dish_types` and `current_dish_type` to the template context.
  - Ensure existing sort and pagination behaviour is unchanged.

- [x] **T2: Update sort buttons to preserve dish_type param**
  - In `templates/accounts/_profile_ratings.html`, update each sort button's `hx-get` URL to append `&dish_type={{ current_dish_type }}`.

- [x] **T3: Add DishType filter bar to template**
  - Above the sort bar, render a filter bar when `dish_types|length > 1`.
  - Include an "All" button (active when `current_dish_type` is empty).
  - Include one button per DishType; mark active when it matches `current_dish_type`.
  - Each button's `hx-get` carries forward `sort={{ current_sort }}&page=1`.

- [x] **T4: Write tests**
  - Test that the fragment returns all ratings when no `dish_type` param is given.
  - Test that the fragment filters correctly for a valid `dish_type` slug.
  - Test that an unknown `dish_type` slug returns all ratings (graceful fallback).
  - Test that `dish_types` in context contains only types the user has actually rated.
  - Test that a user with only one DishType does not have the filter bar rendered.
