from rest_framework import serializers

class SendMessageSerializer(serializers.Serializer):
    receiver = serializers.CharField(required=False, help_text="ID of user,club or event")
    message = serializers.CharField(required=False, help_text="Message")
    reply_id = serializers.CharField(required=False, help_text="ID of message on which user reply")
    forward_id = serializers.CharField(required=False, help_text="Forword message ")


    def validate(self, fields):
        receiver = fields.get("receiver")
        message = fields.get("message")

        if not any([receiver]):
            raise serializers.ValidationError("receiver(s) ID should be present")
        if not any([message]):
            raise serializers.ValidationError("Message, attachment or post should be present")
        return fields