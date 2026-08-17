from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_venuelocation_created_at_updated_at'),
    ]

    operations = [
        # DishType
        migrations.AddField(
            model_name='dishtype',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dishtype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Dish
        migrations.AddField(
            model_name='dish',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dish',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # SavedDish — updated_at only (has saved_at already)
        migrations.AddField(
            model_name='saveddish',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
