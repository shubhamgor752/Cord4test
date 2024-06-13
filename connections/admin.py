from django.contrib import admin
from .models import Connection

# Register your models here.


class ConnectionAdmin(admin.ModelAdmin):
    fields = ["user", "followers" ,"following", "pending_followers"]  
    list_display = ("user", "get_followers_display", "get_following_display", "get_pending_followers")  

    def get_followers_display(self, obj):
        return ', '.join([follower.username for follower in obj.followers.all()])
    get_followers_display.short_description = "Followers"  


    def get_following_display(self,obj):
        return ", ".join([following.username for following in obj.following.all()])
    
    get_following_display.short_description = "Following"

    def get_pending_followers(self,obj):
        return ", ".join([pendingfollower.username for pendingfollower in obj.pending_followers.all()])
    
    get_pending_followers.short_description="Pending Requests" 




admin.site.register(Connection, ConnectionAdmin)


# admin.site.register(Connection)