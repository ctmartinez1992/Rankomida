## Purpose

Define bulk publish and unpublish Django admin actions on the Venue changelist.

## Requirements

### Requirement: Staff can bulk-publish venues from the admin changelist
A staff user SHALL be able to select one or more venues in the Django admin changelist and apply a "Publish selected venues" action that sets `is_published = True` on all selected venues and displays a success message with the count.

#### Scenario: Publishing multiple venues at once
- **WHEN** a staff user selects two or more unpublished venues and chooses "Publish selected venues"
- **THEN** all selected venues SHALL have `is_published` set to `True`
- **AND** the admin SHALL display a message reporting how many venues were published

#### Scenario: Publishing a single venue via action
- **WHEN** a staff user selects one unpublished venue and chooses "Publish selected venues"
- **THEN** that venue SHALL have `is_published` set to `True`
- **AND** the admin SHALL display a singular success message

### Requirement: Staff can bulk-unpublish venues from the admin changelist
A staff user SHALL be able to select one or more venues in the Django admin changelist and apply an "Unpublish selected venues" action that sets `is_published = False` on all selected venues and displays a success message with the count.

#### Scenario: Unpublishing multiple venues at once
- **WHEN** a staff user selects two or more published venues and chooses "Unpublish selected venues"
- **THEN** all selected venues SHALL have `is_published` set to `False`
- **AND** the admin SHALL display a message reporting how many venues were unpublished

#### Scenario: Unpublishing a single venue via action
- **WHEN** a staff user selects one published venue and chooses "Unpublish selected venues"
- **THEN** that venue SHALL have `is_published` set to `False`
- **AND** the admin SHALL display a singular success message
