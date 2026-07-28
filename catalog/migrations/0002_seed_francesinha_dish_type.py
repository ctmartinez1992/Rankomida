from django.db import migrations


def seed_francesinha_dish_type(apps, schema_editor):
    DishType = apps.get_model("catalog", "DishType")
    DishType.objects.get_or_create(
        slug="francesinha",
        defaults={
            "name": "Francesinha",
            "description": "Initial dish type for MVP ranking.",
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_francesinha_dish_type, migrations.RunPython.noop),
    ]
