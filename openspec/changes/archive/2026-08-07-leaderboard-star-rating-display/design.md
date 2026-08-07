## Context

The leaderboard currently shows `sort_score` (a 1–5 average) as a raw number via the `score_as_stars` template filter, which maps the 1–5 scale directly to star glyphs. The goal is to display star glyphs that reflect a 0–100 percentage scale, with the percentage visible on hover — matching the mental model described in the proposal.

The existing `score_as_stars` filter works on the 1–5 input scale. It will remain untouched to avoid breaking other usages (e.g. dish detail pages).

## Goals / Non-Goals

**Goals:**
- Add a `score_as_stars_pct` filter that accepts a 0–100 value and returns star glyphs.
- Update the leaderboard template to convert `sort_score` to a percentage and use the new filter.
- Show the percentage as a hover tooltip on the score badge.

**Non-Goals:**
- Changing how scores are stored or computed.
- Modifying the existing `score_as_stars` filter or other templates that use it.
- Adding animated or CSS-based star components — plain Unicode glyphs are sufficient.

## Decisions

### New filter instead of modifying the existing one
`score_as_stars` is already used on dish detail pages for 1–5 input. Changing its input expectation would break those usages. A new `score_as_stars_pct` filter keeps concerns separate and is explicit at the call site.

**Alternative considered:** Auto-detect scale by value (`> 5` = percentage mode). Rejected because it adds hidden branching and makes the filter harder to reason about.

### Percentage conversion in the template
`sort_score` is converted to a percentage in the template using a `multiply` or inline expression, rather than in the view. The leaderboard view already returns `sort_score` as the canonical value; the display conversion is a presentation concern.

Since Django templates don't support arithmetic directly, a small `multiply` template filter (or reuse of any existing math filter) will be added to `ratings_tags.py` alongside `score_as_stars_pct`.

**Alternative considered:** Convert in the view and pass `sort_score_pct` as a separate annotation. Rejected — unnecessary view complexity for a pure display transformation.

### Tooltip via `title` attribute
The percentage is shown via HTML `title` attribute on the score element. No JavaScript or custom tooltip library needed.

## Risks / Trade-offs

- [Django template arithmetic] → Django templates lack built-in multiplication. A `mul` filter (or equivalent) needs to be added. This is trivial but is an extra surface. → Mitigation: Keep it simple — `score * 20` via a one-liner filter.
- [Rounding] → `sort_score * 20` may produce a float with decimals (e.g. 87.333…). → Mitigation: Round to nearest integer in the filter before display.
