from django.db import models


class DishType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    dish_type = models.ForeignKey(
        DishType,
        on_delete=models.PROTECT,
        related_name="dishes",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="dishes",
    )
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "venue")

    def __str__(self) -> str:
        return f"{self.name} ({self.venue.name})"
