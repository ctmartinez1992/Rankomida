"""Import Porto venues from Google Places API (New) Text Search.

Staff tool. Imported venues are created unpublished and reviewed in admin before
they reach the public site.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from catalog.models import Venue, VenueLocation
from catalog.services.google_places import MAX_PAGES, PlacesError, RequestBudget, fetch_photo, search_text

logger = logging.getLogger(__name__)


DEFAULT_QUERIES = [
    "francesinha Abragão",
    "francesinha Agrela",
    "francesinha Água Longa",
    "francesinha Águas Santas",
    "francesinha Aguçadoura",
    "francesinha Aguiar de Sousa",
    "francesinha Aião",
    "francesinha Airães",
    "francesinha Alfena",
    "francesinha Alpendorada",
    "francesinha Várzea",
    "francesinha Torrão",
    "francesinha Alvarelhos",
    "francesinha Amorim",
    "francesinha Ansiães",
    "francesinha Arcos",
    "francesinha Arcozelo",
    "francesinha Argivai",
    "francesinha Arreigada",
    "francesinha Árvore",
    "francesinha Astromil",
    "francesinha Aveleda",
    "francesinha Aver-o-Mar",
    "francesinha Aves",
    "francesinha Avessadas e Rosém",
    "francesinha Avintes",
    "francesinha Azurara",
    "francesinha Baguim do Monte (Rio Tinto)",
    "francesinha Balazar",
    "francesinha Baltar",
    "francesinha Banho e Carvalhosa",
    "francesinha Barrosas (Santo Estêvão)",
    "francesinha Beire",
    "francesinha Beiriz",
    "francesinha Bem Viver",
    "francesinha Boelhe",
    "francesinha Bonfim",
    "francesinha Bustelo",
    "francesinha Cabeça Santa",
    "francesinha Caíde de Rei",
    "francesinha Campanhã",
    "francesinha Campo",
    "francesinha Candemil",
    "francesinha Canelas",
    "francesinha Canidelo",
    "francesinha Capela",
    "francesinha Carvalhosa",
    "francesinha Castêlo da Maia",
    "francesinha Castelões",
    "francesinha Cete",
    "francesinha Cidade da Maia",
    "francesinha Codessos",
    "francesinha Constance",
    "francesinha Covelas",
    "francesinha Crestuma",
    "francesinha Cristelo",
    "francesinha Croca",
    "francesinha Custóias",
    "francesinha Duas Igrejas",
    "francesinha Duas Igrejas",
    "francesinha Eiriz",
    "francesinha Eja",
    "francesinha Ermesinde",
    "francesinha Estela",
    "francesinha Fajozes",
    "francesinha Ferreira",
    "francesinha Figueiró",
    "francesinha Folgosa",
    "francesinha Fonte Arcada",
    "francesinha Fornelo",
    "francesinha Frazão",
    "francesinha Freamunde",
    "francesinha Fregim",
    "francesinha Frende",
    "francesinha Friande",
    "francesinha Fridão",
    "francesinha Galegos",
    "francesinha Gandra",
    "francesinha Gestaçô",
    "francesinha Gião",
    "francesinha Gondar",
    "francesinha Gouveia (São Simão)",
    "francesinha Gove",
    "francesinha Grijó",
    "francesinha Grilo",
    "francesinha Guidões",
    "francesinha Guifões",
    "francesinha Guilhabreu",
    "francesinha Guilhufe e Urrô",
    "francesinha Gulpilhares",
    "francesinha Idães",
    "francesinha Irivo",
    "francesinha Jazente",
    "francesinha Jugueiros",
    "francesinha Junqueira",
    "francesinha Labruge",
    "francesinha Lagares e Figueira",
    "francesinha Lamoso",
    "francesinha Laundos",
    "francesinha Lavra",
    "francesinha Leça da Palmeira",
    "francesinha Leça do Balio",
    "francesinha Lever",
    "francesinha Lodares",
    "francesinha Loivos do Monte",
    "francesinha Lomba",
    "francesinha Lomba",
    "francesinha Lordelo",
    "francesinha Louredo",
    "francesinha Lufrei",
    "francesinha Lustosa",
    "francesinha Luzim e Vila Cova",
    "francesinha Macieira",
    "francesinha Macieira da Maia",
    "francesinha Madalena",
    "francesinha Mafamude",
    "francesinha Malta",
    "francesinha Mancelos",
    "francesinha Marco",
    "francesinha Matosinhos",
    "francesinha Meinedo",
    "francesinha Meixomil",
    "francesinha Milheirós",
    "francesinha Mindelo",
    "francesinha Modelos",
    "francesinha Modivas",
    "francesinha Monte Córdova",
    "francesinha Moreira",
    "francesinha Muro",
    "francesinha Navais",
    "francesinha Negrelos (São Tomé)",
    "francesinha Nevogilde",
    "francesinha Nogueira e Silva Escura",
    "francesinha Oldrões",
    "francesinha Olival",
    "francesinha Oliveira do Douro",
    "francesinha Paço de Sousa",
    "francesinha Paços de Ferreira",
    "francesinha Paços de Gaiolo",
    "francesinha Padronelo",
    "francesinha Parada de Todeia",
    "francesinha Paranhos",
    "francesinha Paredes",
    "francesinha Paredes de Viadores e Manhuncelos",
    "francesinha Pedroso",
    "francesinha Pedrouços",
    "francesinha Penacova",
    "francesinha Penafiel",
    "francesinha Penamaior",
    "francesinha Penha Longa",
    "francesinha Perafita",
    "francesinha Perosinho",
    "francesinha Perozelo",
    "francesinha Pinheiro",
    "francesinha Pombeiro de Ribavizela",
    "francesinha Póvoa de Varzim",
    "francesinha Raimonda",
    "francesinha Ramalde",
    "francesinha Rans",
    "francesinha Rates",
    "francesinha Rebordelo",
    "francesinha Rebordões",
    "francesinha Rebordosa",
    "francesinha Recarei",
    "francesinha Recezinhos (São Mamede)",
    "francesinha Recezinhos (São Martinho)",
    "francesinha Refontoura",
    "francesinha Regilde",
    "francesinha Reguenga",
    "francesinha Retorta",
    "francesinha Revinhade",
    "francesinha Rio de Moinhos",
    "francesinha Rio Mau",
    "francesinha Rio Mau",
    "francesinha Rio Tinto",
    "francesinha Roriz",
    "francesinha Salvador do Monte",
    "francesinha Sande e São Lourenço do Douro",
    "francesinha Sandim",
    "francesinha Sanfins de Ferreira",
    "francesinha Santa Cruz do Bispo",
    "francesinha Santa Marinha",
    "francesinha Santa Marinha do Zêzere",
    "francesinha Santo Isidoro e Livração",
    "francesinha São Félix da Marinha",
    "francesinha São Mamede de Infesta",
    "francesinha São Pedro da Afurada",
    "francesinha São Pedro Fins",
    "francesinha Sebolido",
    "francesinha Seixezelo",
    "francesinha Sendim",
    "francesinha Senhora da Hora",
    "francesinha Sermonde",
    "francesinha Seroa",
    "francesinha Serzedo",
    "francesinha Soalhães",
    "francesinha Sobrado",
    "francesinha Sobreira",
    "francesinha Sobretâmega",
    "francesinha Sobrosa",
    "francesinha Sousela",
    "francesinha Tabuado",
    "francesinha Telões",
    "francesinha Termas de São Vicente",
    "francesinha Terroso",
    "francesinha Torno",
    "francesinha Tougues",
    "francesinha Travanca",
    "francesinha Aboadela",
    "francesinha Sanche",
    "francesinha Várzea",
    "francesinha Aldoar",
    "francesinha Foz do Douro",
    "francesinha Nevogilde",
    "francesinha Amarante (São Gonçalo)",
    "francesinha Madalena",
    "francesinha Cepelos",
    "francesinha Gatão",
    "francesinha Ancede",
    "francesinha Ribadouro",
    "francesinha Areias",
    "francesinha Sequeiró",
    "francesinha Lama",
    "francesinha Palmeira",
    "francesinha Bagunte",
    "francesinha Ferreiró",
    "francesinha Outeiro Maior",
    "francesinha Parada",
    "francesinha Baião (Santa Leocádia)",
    "francesinha Mesquinhata",
    "francesinha Bougado (São Martinho e Santiago)",
    "francesinha Bustelo",
    "francesinha Carneiro",
    "francesinha Carvalho de Rei",
    "francesinha Campelo",
    "francesinha Ovil",
    "francesinha Carreira",
    "francesinha Refojos de Riba de Ave",
    "francesinha Cedofeita",
    "francesinha Santo Ildefonso",
    "francesinha Sé",
    "francesinha Miragaia",
    "francesinha São Nicolau",
    "francesinha Vitória",
    "francesinha Cernadelo",
    "francesinha Lousada (São Miguel e Santa Margarida)",
    "francesinha Coronado (São Romão e São Mamede)",
    "francesinha Cristelos",
    "francesinha Boim",
    "francesinha Ordem",
    "francesinha Fânzeres",
    "francesinha São Pedro da Cova",
    "francesinha Figueiras",
    "francesinha Covas",
    "francesinha Figueiró (Santiago e Santa Cristina)",
    "francesinha Foz do Sousa",
    "francesinha Covelo",
    "francesinha Freixo de Cima",
    "francesinha Freixo de Baixo",
    "francesinha Gondomar (São Cosme)",
    "francesinha Valbom",
    "francesinha Jovim",
    "francesinha Lamelas",
    "francesinha Guimarei",
    "francesinha Loivos da Ribeira",
    "francesinha Tresouras",
    "francesinha Lordelo do Ouro",
    "francesinha Massarelos",
    "francesinha Macieira da Lixa",
    "francesinha Caramos",
    "francesinha Margaride (Santa Eulália)",
    "francesinha Várzea",
    "francesinha Lagares",
    "francesinha Varziela",
    "francesinha Moure",
    "francesinha Melres",
    "francesinha Medas",
    "francesinha Nespereira",
    "francesinha Casais",
    "francesinha Olo",
    "francesinha Canadelo",
    "francesinha Pedreira",
    "francesinha Rande",
    "francesinha Sernande",
    "francesinha Santa Cruz do Douro",
    "francesinha São Tomé de Covelas",
    "francesinha Santo Tirso",
    "francesinha Couto (Santa Cristina e São Miguel)",
    "francesinha Burgães",
    "francesinha Silvares",
    "francesinha Pias",
    "francesinha Nogueira",
    "francesinha Alvarenga",
    "francesinha Teixeira",
    "francesinha Teixeiró",
    "francesinha Torrados",
    "francesinha Sousa",
    "francesinha Touguinha",
    "francesinha Touguinhó",
    "francesinha Unhão",
    "francesinha Lordelo",
    "francesinha Vila Cova da Lixa",
    "francesinha Borba de Godim",
    "francesinha Vila Fria",
    "francesinha Vizela (São Jorge)",
    "francesinha Vila Garcia",
    "francesinha Aboim",
    "francesinha Chapa",
    "francesinha Vila Verde",
    "francesinha Santão",
    "francesinha Vilar",
    "francesinha Mosteiró",
    "francesinha Vairão",
    "francesinha Valadares",
    "francesinha Valadares",
    "francesinha Valongo",
    "francesinha Valpedre",
    "francesinha Vandoma",
    "francesinha Várzea, Aliviada e Folhada",
    "francesinha Viariz",
    "francesinha Vila Boa de Quires e Maureles",
    "francesinha Vila Boa do Bispo",
    "francesinha Vila Caiz",
    "francesinha Vila Chã",
    "francesinha Vila Chã do Marão",
    "francesinha Vila do Conde",
    "francesinha Vila Meã",
    "francesinha Vila Nova da Telha",
    "francesinha Vila Nova do Campo",
    "francesinha Vilar de Andorinho",
    "francesinha Vilar de Pinheiro",
    "francesinha Vilar do Paraíso",
    "francesinha Vilar do Torno e Alentém",
    "francesinha Vilarinho",
    "francesinha Vilela",
]
DEFAULT_CITY = "Porto"

_COORD_PRECISION = Decimal("0.000001")
_RATING_PRECISION = Decimal("0.1")

# Deliberately excludes administrative_area_level_2: for Portuguese addresses that
# is the municipality, which only duplicates `city`.
_NEIGHBOURHOOD_TYPES = ("sublocality_level_1", "sublocality")


class Command(BaseCommand):
    help = "Import venues from Google Places API (New) Text Search."

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            action="append",
            dest="queries",
            metavar="TEXT",
            help=(
                "Text Search query; repeatable. "
                f"Defaults to {' and '.join(repr(q) for q in DEFAULT_QUERIES)}."
            ),
        )
        parser.add_argument(
            "--city",
            default=DEFAULT_CITY,
            help=f"City to fall back on when Google omits one (default: {DEFAULT_CITY}).",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=MAX_PAGES,
            help=f"Pages to request per query, capped at Google's limit of {MAX_PAGES}.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be written without touching the database.",
        )
        parser.add_argument(
            "--max-requests",
            type=int,
            default=60,
            help=(
                "Maximum total HTTP requests to the Google Maps API per run (default: 60). "
                "Covers text search pages (1 each), photo metadata (1 each), and photo "
                "binary downloads (1 each). Use 0 for unlimited. Re-runs skip venues that "
                "already have photos, so remaining budget goes further on subsequent runs."
            ),
        )

    def handle(self, *args, **options):
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            raise CommandError(
                "GOOGLE_MAPS_API_KEY is not set. Add it to your environment or .env "
                "before running this command."
            )

        queries = options["queries"] or list(DEFAULT_QUERIES)
        city_fallback = options["city"]
        max_pages = options["max_pages"]
        dry_run = options["dry_run"]
        budget = RequestBudget(options["max_requests"])

        logger.debug(
            "places.handle_start queries=%r city=%r max_pages=%d dry_run=%s max_requests=%d",
            queries,
            city_fallback,
            max_pages,
            dry_run,
            options["max_requests"],
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no database writes."))

        seen_place_ids: set[str] = set()
        created = updated = skipped = 0

        for query in queries:
            self.stdout.write(f"Query: {query!r}")
            logger.info("places.query_start query=%r max_pages=%d", query, max_pages)
            try:
                places = list(
                    search_text(
                        query,
                        api_key=api_key,
                        max_pages=max_pages,
                        budget=budget,
                    )
                )
            except PlacesError as exc:
                logger.error("places.query_failed query=%r error=%s", query, exc)
                self.stderr.write(self.style.ERROR(f"  Query failed: {exc}"))
                continue

            logger.info("places.query_done query=%r count=%d", query, len(places))

            for place in places:
                place_id = (place or {}).get("id")
                if not place_id:
                    skipped += 1
                    logger.warning("places.skip reason=missing_id")
                    continue
                if place_id in seen_place_ids:
                    logger.debug("places.skip reason=duplicate place_id=%s", place_id)
                    continue
                seen_place_ids.add(place_id)

                try:
                    outcome = self._process(place, city_fallback, dry_run, api_key, budget)
                except Exception as exc:  # one bad place must not lose the batch
                    skipped += 1
                    logger.exception(
                        "places.skip reason=processing_error place_id=%s error=%s",
                        place_id,
                        exc,
                    )
                    self.stderr.write(self.style.ERROR(f"  Skipped {place_id}: {exc}"))
                    continue

                if outcome == "created":
                    created += 1
                else:
                    updated += 1

        self.stdout.write("")
        verb = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {created}, "
                f"{'would update' if dry_run else 'updated'} {updated}, "
                f"skipped {skipped}."
            )
        )
        logger.info(
            "places.run_complete created=%d updated=%d skipped=%d budget_used=%d",
            created,
            updated,
            skipped,
            budget.used,
        )

    def _process(self, place: dict[str, Any], city_fallback: str, dry_run: bool, api_key: str, budget: RequestBudget) -> str:
        fields = _map_place(place, city_fallback)
        place_id = fields["google_place_id"]
        existing = VenueLocation.objects.filter(google_place_id=place_id).first()

        if existing is not None:
            self.stdout.write(f"  update: {existing.venue.name}")
            if not dry_run:
                self._apply_location_fields(existing, fields)
                logger.info(
                    "places.venue_updated name=%r place_id=%s venue_id=%s",
                    existing.venue.name,
                    place_id,
                    existing.venue_id,
                )
            return "updated"

        name = fields.pop("_name")
        self.stdout.write(f"  create: {name}")
        if not dry_run:
            with transaction.atomic():
                venue = Venue.objects.create(
                    name=name,
                    slug=_unique_slug(name),
                    city=fields["city"],
                    is_published=False,
                    source=Venue.SOURCE_GOOGLE,
                )
                location = VenueLocation(venue=venue)
                self._apply_location_fields(location, fields)
            logger.info(
                "places.venue_created name=%r place_id=%s venue_id=%s",
                name,
                place_id,
                venue.pk,
            )
            if not venue.photo:
                self._fetch_and_save_photo(venue, place, api_key, budget)
        else:
            logger.debug("places.dry_run action=create name=%r place_id=%s", name, place_id)
        return "created"

    def _fetch_and_save_photo(self, venue: Venue, place: dict[str, Any], api_key: str, budget: RequestBudget) -> None:
        photos = place.get("photos") or []
        if not photos:
            logger.debug("places.photo_skip reason=no_photos venue_id=%s", venue.pk)
            return
        photo_name = photos[0].get("name") if isinstance(photos[0], dict) else None
        if not photo_name:
            logger.debug("places.photo_skip reason=no_photo_name venue_id=%s", venue.pk)
            return
        # Each photo fetch costs 2 API calls (metadata GET + binary GET).
        if not budget.consume(2):
            logger.warning("places.photo_budget_exhausted venue_id=%s", venue.pk)
            return
        try:
            image_bytes = fetch_photo(photo_name, api_key=api_key)
        except (PlacesError, requests.RequestException) as exc:
            logger.warning("places.photo_skip venue_id=%s error=%s", venue.pk, exc)
            return
        ext = "jpg"
        filename = f"venue_{venue.pk}.{ext}"
        venue.photo.save(filename, ContentFile(image_bytes), save=False)
        venue.photo_credit = "Google Maps"
        venue.photo_source_url = place.get("googleMapsUri") or ""
        venue.save(update_fields=["photo", "photo_credit", "photo_source_url"])
        logger.debug("places.photo_saved venue_id=%s filename=%s", venue.pk, filename)

    @staticmethod
    def _apply_location_fields(location: VenueLocation, fields: dict[str, Any]) -> None:
        """Write Google-sourced fields only; `name` stays whatever staff set."""
        for key, value in fields.items():
            if key.startswith("_"):
                continue
            setattr(location, key, value)
        location.last_synced_at = timezone.now()
        location.save()


def _map_place(place: dict[str, Any], city_fallback: str) -> dict[str, Any]:
    components = place.get("addressComponents") or []
    city = _component(components, "locality") or city_fallback
    name = _text(place.get("displayName")) or ""
    if not name:
        raise ValueError("place has no display name")

    location = place.get("location") or {}
    hours = place.get("regularOpeningHours")

    return {
        "_name": name[:200],
        "google_place_id": place["id"],
        "city": city[:120],
        "address": (place.get("formattedAddress") or "")[:255],
        "latitude": _decimal(location.get("latitude"), _COORD_PRECISION),
        "longitude": _decimal(location.get("longitude"), _COORD_PRECISION),
        "postal_code": (_component(components, "postal_code") or "")[:20],
        "neighbourhood": _neighbourhood(components)[:120],
        "business_status": (place.get("businessStatus") or "")[:32],
        "phone": (place.get("nationalPhoneNumber") or "")[:40],
        "website_url": (place.get("websiteUri") or "")[:500],
        "google_maps_uri": (place.get("googleMapsUri") or "")[:500],
        "price_level": (place.get("priceLevel") or "")[:32],
        "primary_type": (place.get("primaryType") or "")[:80],
        "types": place.get("types") or [],
        "opening_hours": hours if isinstance(hours, dict) else None,
        "google_rating": _decimal(place.get("rating"), _RATING_PRECISION),
        "google_user_rating_count": place.get("userRatingCount"),
    }


def _text(value: Any) -> str:
    if isinstance(value, dict):
        return value.get("text") or ""
    return value or ""


def _component(components: list[dict[str, Any]], wanted: str) -> str:
    for component in components:
        if wanted in (component.get("types") or []):
            return component.get("longText") or component.get("shortText") or ""
    return ""


def _neighbourhood(components: list[dict[str, Any]]) -> str:
    for wanted in _NEIGHBOURHOOD_TYPES:
        found = _component(components, wanted)
        if found:
            return found
    return ""


def _decimal(value: Any, precision: Decimal) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value)).quantize(precision)
    except (InvalidOperation, ValueError):
        return None


def _unique_slug(name: str) -> str:
    base = slugify(name)[:210] or "venue"
    candidate = base
    suffix = 2
    taken = set(Venue.objects.filter(slug__startswith=base).values_list("slug", flat=True))
    while candidate in taken:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
