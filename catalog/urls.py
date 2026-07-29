from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.DishTypeListView.as_view(), name="list"),
    path("dishes/<slug:type_slug>/", views.DishByTypeView.as_view(), name="by_type"),
    path("dishes/<slug:type_slug>/<slug:slug>/", views.DishDetailView.as_view(), name="detail"),
]
