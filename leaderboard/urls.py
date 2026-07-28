from django.urls import path

from .views import LeaderboardListView

app_name = "leaderboard"

urlpatterns = [
    path("", LeaderboardListView.as_view(), name="list"),
    path("<slug:dish_type_slug>/", LeaderboardListView.as_view(), name="by_dish_type"),
]
