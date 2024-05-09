from rest_framework import serializers
from chat.models import ChatMessage
from .models import UserProfile  # Import the UserProfile mod
class SendMessageSerializer(serializers.Serializer):
    receiver = serializers.CharField(required=False, help_text="ID of user")
    message = serializers.CharField(required=False, help_text="Message")
    forward_id = serializers.CharField(required=False, help_text="Forword message ")
    media = serializers.ImageField(required=False, help_text="Media attachment")
    schedule_time = serializers.DateTimeField(required=False)

    #   for message edit
    message_id = serializers.CharField(required=False, help_text="ID of message")

    def validate(self, fields):
        receiver = fields.get("receiver")
        message = fields.get("message")
        media = fields.get("media")

        if not any([receiver]):
            raise serializers.ValidationError("receiver(s) ID should be present")
        if not any([message, media]):
            raise serializers.ValidationError("Message, attachment or post should be present")
        return fields


class EditMessageSerializer(serializers.Serializer):
    #   for message edit
    message_id = serializers.CharField(required=False, help_text="ID of message")
    message = serializers.CharField(required=False, help_text="New Message")


class SuggestionMessageSerializer(serializers.Serializer):
    message_id = serializers.CharField(required=False, help_text="ID of message")
    receiver = serializers.CharField(required=False, help_text="Forword message ")


class MyConversationSerializer(serializers.Serializer):

    sender = serializers.SerializerMethodField(required=False)
    receiver = serializers.SerializerMethodField(required=False)
    message = serializers.SerializerMethodField(required=False)

    def get_sender(self, obj):
        try:
            return obj.sender.username
        except:
            return None

    def get_receiver(self, obj):
        try:
            return obj.receiver.username
        except:
            return None

    def get_message(self, obj):
        try:
            return obj.message
        except:
            return None
