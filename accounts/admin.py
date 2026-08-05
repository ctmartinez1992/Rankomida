from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "is_public"]
    list_filter = ["is_public"]
    search_fields = ["user__username"]
