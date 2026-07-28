from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("leaderboard", "0002_alter_dishaggregatescore_options_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="DishAggregateScore",
        ),
    ]
