from django.contrib import admin
from register.models import UserProfile, CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name","is_private","is_superuser")
    fields = [
        "username",
        "first_name",
        "is_private"
        "is_superuser",
    ]


admin.site.register(CustomUser, CustomUserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    fields = [
        "username",
        "first_name",
        "profession",
        "bio",
        "phone_number",
        "email",
        "date_of_birth",
        "is_superuser",
    ]
    list_display = (
        "id",
        "username",
        "first_name",
        "phone_number",
        "bio",
        "email",
        "date_of_birth",
    )
    search_fields = ("username", "first_name", "phone_number")


admin.site.register(UserProfile, UserProfileAdmin)
