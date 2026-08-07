## ADDED Requirements

### Requirement: Filter and sort controls use select dropdowns
Filter and sort controls in the ratings and community notes fragments SHALL be rendered as native `<select>` elements, not pill buttons.

#### Scenario: Sort dropdown renders current selection
- **WHEN** the community notes or profile ratings fragment loads
- **THEN** the sort `<select>` SHALL have the currently active sort value pre-selected

#### Scenario: Dish-type dropdown renders current selection
- **WHEN** the profile ratings fragment loads
- **THEN** the dish-type `<select>` SHALL have the currently active dish_type pre-selected (or "All" if none)

### Requirement: Select labels are external
Each `<select>` control SHALL have a visible `<label>` element rendered outside (before) the `<select>`, in the same flex row.

#### Scenario: Sort label visible
- **WHEN** a fragment containing a sort control is rendered
- **THEN** a label reading "Sort by" SHALL appear adjacent to the sort `<select>`

#### Scenario: Dish-type label visible
- **WHEN** the profile ratings fragment contains a dish-type filter
- **THEN** a label reading "Dish type" SHALL appear adjacent to the dish-type `<select>`

### Requirement: Select triggers HTMX request on change
Selecting an option from a filter or sort `<select>` SHALL immediately fire an HTMX GET request with the new value as a query parameter.

#### Scenario: Sort change fires request
- **WHEN** the user selects a different sort option
- **THEN** an HTMX GET request SHALL fire with `sort=<new_value>&page=1`

#### Scenario: Dish-type change fires request
- **WHEN** the user selects a different dish type option
- **THEN** an HTMX GET request SHALL fire with `dish_type=<slug>&sort=<current_sort>&page=1`

#### Scenario: Sort preserves dish-type
- **WHEN** the user changes the sort dropdown while a dish type is selected
- **THEN** the HTMX request SHALL include the current `dish_type` value

#### Scenario: Dish-type preserves sort
- **WHEN** the user changes the dish-type dropdown while a sort is active
- **THEN** the HTMX request SHALL include the current `sort` value
