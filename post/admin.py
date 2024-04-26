from django.contrib import admin
from .models import Post,Comment

# Register your models here.


class postadmin(admin.ModelAdmin):
    fields = ["id", "author", "likes","description"]
    list_display = ['id','author','get_like_display','description']


    def get_like_display(self,obj):
        return ", ".join(like.username for like in obj.likes.all())
    
    get_like_display.short_description = 'Likes'

admin.site.register(Post,postadmin)



class commentadmin(admin.ModelAdmin):
    fields = ["post","comment","author"]

    list_display = ["post","comment", "author"]



admin.site.register(Comment,commentadmin)