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
        "places.photos",
        "nextPageToken",
    ]
)

PHOTO_BASE_URL = "https://places.googleapis.com/v1/{name}/media"

MAX_PAGES = 3
MAX_PAGE_SIZE = 20
REQUEST_TIMEOUT = 30
# A freshly issued page token is rejected for a few seconds before it resolves.
PAGE_TOKEN_DELAY = 2.0
PAGE_TOKEN_ATTEMPTS = 4


class PlacesError(RuntimeError):
    """The Places API could not be reached or returned an error."""


class RequestBudget:
    """Tracks and enforces a cap on HTTP requests to the Google Maps API.

    Pass ``limit=0`` for unlimited requests.
    """

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._used = 0

    def consume(self, n: int = 1) -> bool:
        """Attempt to consume *n* requests from the budget.

        Returns ``True`` if the requests are allowed and records them.
        Returns ``False`` (without recording) when the budget is exhausted.
        """
        if self._limit == 0:
            self._used += n
            return True
        if self._used + n > self._limit:
            return False
        self._used += n
        return True

    @property
    def used(self) -> int:
        return self._used

    @property
    def exhausted(self) -> bool:
        return self._limit > 0 and self._used >= self._limit


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
    budget: RequestBudget | None = None,
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
        if budget is not None and not budget.consume(1):
            logger.warning("places.budget_exhausted stopping_before_page=%s", page + 1)
            break

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


def fetch_photo(
    photo_name: str,
    *,
    api_key: str,
    max_width: int = 800,
    session: requests.Session | None = None,
) -> bytes:
    """Download a photo binary from the Places Photo API.

    ``photo_name`` is the resource path returned in a place's ``photos`` array
    (e.g. ``places/ChIJ.../photos/AXCi...``).  Returns the raw image bytes.
    Raises :exc:`PlacesError` on any API or network failure.
    """
    http = session or requests.Session()
    url = PHOTO_BASE_URL.format(name=photo_name)
    params = {
        "key": api_key,
        "maxWidthPx": max_width,
        "skipHttpRedirect": "true",
    }
    try:
        meta_response = http.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise PlacesError(f"Photo metadata request failed: {exc}") from exc

    if meta_response.status_code != 200:
        raise PlacesError(
            f"Photo metadata returned HTTP {meta_response.status_code}: "
            f"{_error_message(meta_response)}"
        )

    try:
        photo_uri = meta_response.json().get("photoUri")
    except ValueError as exc:
        raise PlacesError("Photo metadata returned a non-JSON response.") from exc

    if not photo_uri:
        raise PlacesError("Photo metadata response contained no photoUri.")

    try:
        image_response = http.get(photo_uri, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise PlacesError(f"Photo download failed: {exc}") from exc

    if image_response.status_code != 200:
        raise PlacesError(
            f"Photo download returned HTTP {image_response.status_code}."
        )

    return image_response.content


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
