from django.db import models
from Register.models import CustomUser
# Create your models here.


class CustomGroup(models.Model):
    id = models.AutoField(primary_key=True)
    group_name = models.TextField()
    group_admins = models.ManyToManyField(CustomUser,related_name= 'group_admin')
    members = models.ManyToManyField(CustomUser, related_name='group_member')
    is_private = models.BooleanField(default=True)
    join_requests = models.ManyToManyField(
        CustomUser, related_name="join_requests", blank=True
    )
    
    def __str__(self):
        return self.group_name 
    



class GroupChat(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name='group_chats')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Group: {self.group}, Sender: {self.sender}, Message: {self.message_content[:50]}..."