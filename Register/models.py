from django.db import models
from django.contrib.auth.models import AbstractUser , AbstractBaseUser
import uuid
from django.utils import timezone
from datetime import timedelta


# Create your models here.
PROFILE_IMAGE = "profile.jpeg"

class CustomUser(AbstractUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)
    bio = models.CharField(max_length=1024, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    # profile_image = models.URLField(max_length=1024, default=PROFILE_IMAGE)
    pin = models.CharField(max_length=6, null=True, blank=True)




    class Meta:
        verbose_name = "custom user"
        verbose_name_plural = "Custom users"


class UserProfile(CustomUser):
    phone_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    profession = models.CharField(max_length=256, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

    def __str__(self) -> str:
        if self.first_name:
            return self.first_name
        else:
            return self.username



class OTPRequest(models.Model):
    mobile_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=300)