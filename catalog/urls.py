from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.DishListView.as_view(), name="list"),
    path("dishes/<slug:slug>/", views.DishDetailView.as_view(), name="detail"),
]
