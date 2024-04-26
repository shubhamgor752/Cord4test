from django.db import models
from Register.models import UserProfile,CustomUser

# Create your models here.


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE , related_name='create_post')
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    description = models.TextField()



class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True)



