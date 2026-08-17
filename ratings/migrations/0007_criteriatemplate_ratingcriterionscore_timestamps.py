from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0006_alter_criteriatemplate_min_score'),
    ]

    operations = [
        # CriteriaTemplate
        migrations.AddField(
            model_name='criteriatemplate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='criteriatemplate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # RatingCriterionScore
        migrations.AddField(
            model_name='ratingcriterionscore',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ratingcriterionscore',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
