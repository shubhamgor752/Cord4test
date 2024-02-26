from django.shortcuts import render

# Create your views here.
import uuid, json
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.serializers import (
    SendMessageSerializer
)
from Register.models import UserProfile
# from administration.utils import user_information

from chat.models import ChatMessage
import uuid
from django.core.exceptions import ObjectDoesNotExist




class SendMessageViewSet(viewsets.ViewSet):
  
    permission_classes = (IsAuthenticated,)
    serializer_class = SendMessageSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                request_data = serializer.validated_data
                current_user = request.user
                receiver_id = request_data.get("receiver")
                message = request_data.get("message")
                reply_id = request_data.get("reply_id")
                forward_id = request_data.get("forward_id")

                if not receiver_id:
                    raise serializers.ValidationError("Receiver ID should be present")

                if not message:
                    raise serializers.ValidationError("Message should be present")

                if forward_id:
                    try:
                        # Retrieve the message to be forwarded
                        forwarded_message = ChatMessage.objects.get(id=forward_id)
                    except ChatMessage.DoesNotExist:
                        raise serializers.ValidationError("Forwarded message does not exist")

                    message_response = ChatMessage.objects.create(
                        sender=request.user.userprofile,  
                        receiver_id=receiver_id,
                        message=forwarded_message.message,  # Copy the message content
                        forwarded_by=request.user.userprofile  # Store the forwarding user's username
                    )
                    return Response(
                        {"status": True, "message": "Message forwarded successfully", "data": serializer.data},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    message_response = ChatMessage.objects.create(
                        sender=request.user.userprofile,  
                        receiver_id=receiver_id,
                        message=message,
                    )
                    return Response(
                        {"status": True, "message": "Message sent successfully", "data": serializer.data},
                        status=status.HTTP_201_CREATED,
                    )
            else:
                return Response(
                    {"status": False, "message": serializer.errors, "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )