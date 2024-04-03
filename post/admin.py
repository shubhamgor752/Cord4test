from django.contrib import admin
from .models import Post

# Register your models here.


class postadmin(admin.ModelAdmin):
    fields = ["author", "description"]
    list_display = ['author', 'description']


admin.site.register(Post,postadmin)