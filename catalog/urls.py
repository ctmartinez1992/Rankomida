from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.DishTypeListView.as_view(), name="list"),
    path("saved/", views.SavedDishListView.as_view(), name="saved"),
    path("venues/", views.VenueListView.as_view(), name="venue_list"),
    path("venues/suggest/", views.VenueSuggestionCreateView.as_view(), name="suggest_venue"),
    path("venues/suggest/thanks/", TemplateView.as_view(template_name="catalog/suggest_venue_success.html"), name="suggest_venue_thanks"),
    path("venues/<slug:slug>/", views.VenueDetailView.as_view(), name="venue_detail"),
    path(
        "venues/<slug:slug>/locations/<int:pk>/",
        views.VenueLocationDetailView.as_view(),
        name="venue_location_detail",
    ),
    path("dishes/<slug:slug>/save/", views.save_dish, name="save"),
    path("dishes/<slug:slug>/unsave/", views.unsave_dish, name="unsave"),
    path("dishes/<slug:type_slug>/", views.DishByTypeView.as_view(), name="by_type"),
    path("dishes/<slug:type_slug>/<slug:slug>/", views.DishDetailView.as_view(), name="detail"),
    path("dishes/<slug:type_slug>/<slug:slug>/notes/", views.CommunityNotesFragmentView.as_view(), name="community_notes_fragment"),
]
