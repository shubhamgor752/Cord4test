from django.db import models
from Register.models import UserProfile

# Create your models here.




class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    media = models.ImageField(upload_to='chat_media/',null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    forwarded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='forwarded_messages', null=True, blank=True)

    class Meta:
        verbose_name = "chat system"
        verbose_name_plural = "chat systems"

    def __str__(self):
        return f"From: {self.sender} | To: {self.receiver} | Message: {self.message[:50]}..."