from django.db import models
from Register.models import UserProfile  # adjust if your user model is different

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('invite', 'Group Invite'),
    ]

    type = models.CharField(choices=NOTIFICATION_TYPES, max_length=10)
    sender = models.ForeignKey(UserProfile, related_name='sent_notifications', on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserProfile, related_name='received_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.type})"
