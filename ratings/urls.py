from django.urls import path

from . import views

app_name = "ratings"

urlpatterns = [
    path("dishes/<slug:slug>/rate/", views.submit_rating, name="submit"),
]
