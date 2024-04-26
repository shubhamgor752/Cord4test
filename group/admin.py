from django.contrib import admin
from .models import CustomGroup , GroupChat


# Register your models here.


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id','group_name', 'get_group_admins', 'get_display_members','is_private','get_join_request')
    fields = ['group_name', 'group_admins', 'members','join_requests']

    def get_display_members(self, obj):
        return ", ".join([member.username for member in obj.members.all()])

    get_display_members.short_description = "Members"

    def get_group_admins(self, obj):
        return ", ".join([member.username for member in obj.group_admins.all()])

    get_group_admins.short_description = "GroupAdmin"



    def get_join_request(self, obj):
        return ", ".join([member.username for member in obj.join_requests.all()])

    get_join_request.short_description = "JoinRequest"

admin.site.register(CustomGroup, GroupAdmin)




class Groupchatadmin(admin.ModelAdmin):

    list_display = ('group', 'sender' ,'message_content','timestamp')

    fields = ['group', 'sender', 'message_content']


admin.site.register(GroupChat, Groupchatadmin)