from django.contrib.auth import views as auth_views
from django.urls import path

from .views import profile, profile_settings, register

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/me/settings/", profile_settings, name="profile_settings"),
    path("profile/<str:username>/", profile, name="profile"),
]
