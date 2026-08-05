from django.db import migrations


def migrate_venue_locations(apps, schema_editor):
    Venue = apps.get_model("catalog", "Venue")
    VenueLocation = apps.get_model("catalog", "VenueLocation")
    for venue in Venue.objects.all():
        if venue.latitude is not None or venue.address:
            VenueLocation.objects.create(
                venue=venue,
                city=venue.city,
                address=venue.address or "",
                latitude=venue.latitude,
                longitude=venue.longitude,
            )


def reverse_migrate_venue_locations(apps, schema_editor):
    VenueLocation = apps.get_model("catalog", "VenueLocation")
    VenueLocation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_add_venuelocation"),
    ]

    operations = [
        migrations.RunPython(
            migrate_venue_locations,
            reverse_migrate_venue_locations,
        ),
    ]
