"""Client for the Google Places API (New) Text Search endpoint.

Only covers what the venue import needs. Google caps a search at 20 results per
page over 3 pages, so 60 results per query is the ceiling regardless of how many
places actually match.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Iterator

import requests

logger = logging.getLogger(__name__)

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# The field mask determines which billing SKU a request falls under, so it is
# kept as one reviewable constant rather than assembled per call.
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.addressComponents",
        "places.location",
        "places.businessStatus",
        "places.primaryType",
        "places.types",
        "places.priceLevel",
        "places.regularOpeningHours",
        "places.nationalPhoneNumber",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.rating",
        "places.userRatingCount",
        "nextPageToken",
    ]
)

MAX_PAGES = 3
MAX_PAGE_SIZE = 20
REQUEST_TIMEOUT = 30
# A freshly issued page token is rejected for a few seconds before it resolves.
PAGE_TOKEN_DELAY = 2.0
PAGE_TOKEN_ATTEMPTS = 4


class PlacesError(RuntimeError):
    """The Places API could not be reached or returned an error."""


def search_text(
    query: str,
    *,
    api_key: str,
    language_code: str = "pt-PT",
    region_code: str = "PT",
    page_size: int = MAX_PAGE_SIZE,
    max_pages: int = MAX_PAGES,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Iterator[dict[str, Any]]:
    """Yield places matching ``query``, following page tokens up to ``max_pages``."""
    if not api_key:
        raise PlacesError("A Google Maps API key is required.")

    http = session or requests.Session()
    pages = max(1, min(max_pages, MAX_PAGES))
    payload_base = {
        "textQuery": query,
        "languageCode": language_code,
        "regionCode": region_code,
        "pageSize": max(1, min(page_size, MAX_PAGE_SIZE)),
    }

    token: str | None = None
    for page in range(pages):
        payload = dict(payload_base)
        if token:
            payload["pageToken"] = token
            sleep(PAGE_TOKEN_DELAY)

        data = _post(http, payload, api_key, is_paged=bool(token), sleep=sleep)
        places = data.get("places") or []
        logger.info(
            "places.search query=%r page=%s results=%s", query, page + 1, len(places)
        )
        yield from places

        token = data.get("nextPageToken")
        if not token:
            break


def _post(
    http: requests.Session,
    payload: dict[str, Any],
    api_key: str,
    *,
    is_paged: bool,
    sleep: Callable[[float], None],
) -> dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    attempts = PAGE_TOKEN_ATTEMPTS if is_paged else 1
    delay = PAGE_TOKEN_DELAY
    last_message = ""

    for attempt in range(1, attempts + 1):
        try:
            response = http.post(
                TEXT_SEARCH_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
            )
        except requests.RequestException as exc:
            raise PlacesError(f"Places request failed: {exc}") from exc

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as exc:
                raise PlacesError("Places returned a non-JSON response.") from exc

        last_message = _error_message(response)
        # A 400 on a paged request usually means the token has not resolved yet.
        if is_paged and response.status_code == 400 and attempt < attempts:
            logger.warning(
                "places.page_token_not_ready attempt=%s retry_in=%ss", attempt, delay
            )
            sleep(delay)
            delay *= 2
            continue

        raise PlacesError(
            f"Places returned HTTP {response.status_code}: {last_message}"
        )

    raise PlacesError(f"Page token never became valid: {last_message}")


def _error_message(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:200]
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            return str(error.get("message") or error)
    return str(body)[:200]
