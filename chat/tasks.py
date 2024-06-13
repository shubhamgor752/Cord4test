# tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from .models import ChatMessage

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_message(sender_id, receiver_id, message, media):
    try:
        # Log task start
        logger.info("Sending scheduled message task started")

        # Create ChatMessage instance
        scheduled_message = ChatMessage.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            media=media,
            # scheduled_time will be set automatically
        )

        # Log message creation
        logger.info(f"Message saved: {scheduled_message}")

        # Log task completion
        logger.info("Sending scheduled message task completed")

        return scheduled_message
    except Exception as e:
        # Log any exceptions
        logger.error(f"Error saving message: {e}")
        return None
