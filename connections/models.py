from typing import Any
from django.db import models
from Register.models import UserProfile
# Create your models here.


class Connection(models.Model):
    """
    AI is creating a summary for Connection.

    Args:
        ConnectionsModel: A model used for managing follow and following relationships between users.

    Returns:
        dict: A dictionary containing the summary of connections.
    """


    user = models.OneToOneField(UserProfile,on_delete=models.CASCADE)
    followers = models.ManyToManyField(UserProfile,related_name="following",blank=True)
    following = models.ManyToManyField(UserProfile,related_name="followers",blank=True)
    pending_followers = models.ManyToManyField(UserProfile,related_name="pending_followers",blank=True)


    def __str__(self) -> str:
        return f"{self.user}"
    

    def get_followers(self):
        # Your logic to retrieve followers
        return self.followers.all()  
    



    