## REMOVED Requirements

### Requirement: Import photo fetching is capped per run
**Reason**: Superseded by the `google-api-request-budget` capability which caps all Google API requests (search + photo) via a single `--max-requests` argument. A separate `--max-photos` limit is redundant and confusing alongside `--max-requests`.
**Migration**: Replace `--max-photos N` with `--max-requests N` (note: photo fetching uses 2 requests per venue, plus search pages use 1 each).
