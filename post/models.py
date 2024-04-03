from django.db import models
from Register.models import UserProfile,CustomUser

# Create your models here.


class Post(models.Model):

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE , related_name='create_post')

    description = models.TextField()

