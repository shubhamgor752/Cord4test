from .models import Notification

def create_notification(sender, receiver, type, message, url=None):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        type=type,
        message=message,
        url=url
    )
