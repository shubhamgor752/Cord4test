from rest_framework import serializers
from chat.models import ChatMessage

class SendMessageSerializer(serializers.Serializer):
    receiver = serializers.CharField(required=False, help_text="ID of user")
    message = serializers.CharField(required=False, help_text="Message")
    forward_id = serializers.CharField(required=False, help_text="Forword message ")
    media = serializers.ImageField(required=False, help_text="Media attachment")


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