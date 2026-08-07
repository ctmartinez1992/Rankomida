# Design: Profile DishType Filter

## URL / Query Param Contract

The fragment URL gains one new optional param:

```
GET /accounts/<username>/ratings/?sort=newest&dish_type=francesinha&page=1
```

| Param       | Values                        | Default |
|-------------|-------------------------------|---------|
| `sort`      | newest / oldest / highest / lowest | newest |
| `dish_type` | any active DishType slug, or absent | (all)  |
| `page`      | integer                       | 1       |

Unknown `dish_type` slugs are silently ignored (fall back to "all").

## View Logic

```
dish_type_slug = request.GET.get("dish_type", "")

qs = RatingSubmission.objects.filter(user=profile_user)
if dish_type_slug:
    qs = qs.filter(dish__dish_type__slug=dish_type_slug)

# Build filter options from user's actual ratings (distinct dish types)
dish_types = (
    DishType.objects
    .filter(dish__ratingsubmission__user=profile_user, is_active=True)
    .distinct()
    .order_by("name")
)
```

Pass to template:
- `dish_types` — queryset for building filter buttons
- `current_dish_type` — the active slug (or `""` for All)

## Template Structure

```
┌────────────────────────────────────────────────────────┐
│  FILTER BY TYPE                                        │
│  [All]  [Francesinha]  [Prego]                        │  ← new
├────────────────────────────────────────────────────────┤
│  SORT                                                  │
│  [Newest]  [Oldest]  [Highest]  [Lowest]              │  ← existing
└────────────────────────────────────────────────────────┘
```

Each filter button is an HTMX button mirroring the sort bar pattern:

```html
hx-get="...?sort={{ current_sort }}&dish_type=&page=1"   <!-- All -->
hx-get="...?sort={{ current_sort }}&dish_type=francesinha&page=1"
```

Sorting buttons carry forward the current dish_type param as well.

## No Model Changes

All filtering is done via ORM traversal through existing FK relationships:
`RatingSubmission → Dish → DishType`. No migrations required.
