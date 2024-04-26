from django.contrib import admin
from .models import ChatMessage
# Register your models here.



# admin.site.register(ChatMessage)


class Userchat(admin.ModelAdmin):
    fields = [
        "sender",
        "receiver",
        # "media",
        "message",
        "forwarded_by",
    ]
    list_display = (
        "id",
        "sender",
        "receiver",
        "message",
        "suggested_message",
        "forwarded_by"
    )


admin.site.register(ChatMessage, Userchat)