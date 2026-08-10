## Context

Rankomida is a Django 6 / SQLite project where users rate dishes across configurable per-type criteria. Scores are currently stored as `DecimalField` values on a 1–10 scale and displayed as a percentage. The form renders criterion fields generically with no special UI treatment — users type a number into an `<input type="number">`.

The `RatingSubmissionForm` is not a ModelForm; it builds criterion fields dynamically from `CriteriaTemplate` rows. Scores flow from form → `RatingSubmission.overall_score` + `RatingCriterionScore.score`. Display happens through the `score_as_percentage` template filter loaded in three templates (dish detail, leaderboard, profile).

## Goals / Non-Goals

**Goals:**
- Replace all numeric score inputs with an interactive half-star widget (1–5 in 0.5 steps)
- Keep the widget dependency-free (no JavaScript, no third-party libraries)
- Update score display across all templates to render star glyphs
- Tighten model and form validation to enforce the new scale

**Non-Goals:**
- Data migration of existing `RatingSubmission` / `RatingCriterionScore` rows
- Animated or hover-preview star effects (can be added later)
- Per-criterion configurable ranges (all criteria use 1–5 going forward)

## Decisions

### D1: CSS-only star widget using radio inputs

**Decision**: Render each star position as two `<input type="radio">` elements (one for the whole value, one for the half value) styled with CSS `clip-path` or `float`/`overflow` to show left/right halves.

**Rationale**: No JavaScript means no JS bundle, no hydration, progressive enhancement by default. The radio-group approach gives native form semantics — the browser submits the value, and Django sees it as a normal POST parameter.

**Alternatives considered**:
- JS-based widget (React component, Alpine.js) — rejected: unnecessary dependency, complicates the no-build setup
- Range input `<input type="range" min="1" max="5" step="0.5">` — rejected: poor cross-browser visual consistency, requires JS to map to stars

**Implementation sketch**:
```
For a star group named "overall_score":
  <div class="star-widget" role="radiogroup">
    <!-- Star 1 -->
    <input type="radio" name="overall_score" id="overall_score_1_half" value="0.5">  <!-- half star -->
    <label for="overall_score_1_half" class="star-half">½</label>
    <input type="radio" name="overall_score" id="overall_score_1"      value="1">    <!-- full star -->
    <label for="overall_score_1"      class="star-full">★</label>
    <!-- ... stars 2–5 ... -->
  </div>
```
CSS uses sibling selectors (`input:checked ~ label`) to fill/unfill stars.

> **Note**: The minimum allowed value is 1 (not 0.5). The `0.5` radio input for star 1 should be omitted or disabled to enforce the 1–5 floor. See `star-rating-input` spec.

### D2: Custom Django Field + Widget

**Decision**: Introduce `StarRatingField(ChoiceField)` and `StarRatingWidget` in `ratings/widgets.py`.

- `StarRatingWidget.render()` emits the `<div class="star-widget">` HTML
- `StarRatingField` holds `CHOICES = [(Decimal("1"), "1"), (Decimal("1.5"), "1.5"), ..., (Decimal("5"), "5")]` and coerces the submitted string to `Decimal`
- `RatingSubmissionForm` uses `StarRatingField` for `overall_score` and each criterion field

**Rationale**: Keeps the form/field/widget layering Django-idiomatic. The field handles validation (valid choice), the widget handles rendering. No template changes are needed to the generic `{% for field in form %}` loop — the widget renders itself.

### D3: Replace `score_as_percentage` with `score_as_stars`

**Decision**: Add `score_as_stars` filter that converts a Decimal to a glyph string (e.g. `Decimal("3.5")` → `"★★★½☆☆"`). Keep the old filter as a private/internal name until all call sites are updated, then remove it.

**Rationale**: Percentages are meaningless in a 1–5 star context. Star glyphs are immediately readable and consistent with the widget UX.

**Format**: filled stars (★) for whole values, a half-star glyph (½ or ⯨) for 0.5 remainder, empty stars (☆) for the remainder up to 5.

### D4: Validation at two layers

- **Form layer** (`StarRatingField`): validates submitted value is one of the nine choices — rejects anything outside 1–5 in 0.5 steps before it touches the database
- **Model layer** (`RatingCriterionScore.clean()`): validates the stored `score` is one of the nine values — guards against direct ORM writes

`CriteriaTemplate.min_score` / `max_score` default to 1.0/5.0. The range-check in `RatingCriterionScore.clean()` is replaced with a set-membership check.

## Risks / Trade-offs

- **CSS browser support**: The sibling-selector star trick works in all modern browsers. IE11 is not supported (consistent with the rest of the project).
- **Accessibility**: Radio inputs are inherently keyboard-navigable and screen-reader friendly when properly labelled. The star glyph labels (`aria-label`) must describe the value (e.g. "3.5 stars") not just the symbol.
- **Existing data**: Scores outside 1–5 remain in the DB. Display code (`score_as_stars`) must handle out-of-range values gracefully (clamp or return "–").
- **`overall_score` stays user-entered**: It is not derived from criterion scores. This is a deliberate scope decision — a weighted composite score is a future concern tracked in `RANKING_OVERALL_WEIGHT`.

## Migration Plan

1. Run `python manage.py makemigrations ratings` after updating `CriteriaTemplate` defaults — generates a schema migration only (default value change).
2. Apply migrations on deploy: `python manage.py migrate`.
3. No data migration needed. Existing ratings remain valid (even if outside 1–5); they display via `score_as_stars` with clamping.
4. Rollback: revert code + migration; old data is unaffected.

## Open Questions

- None — all decisions above are resolved.
