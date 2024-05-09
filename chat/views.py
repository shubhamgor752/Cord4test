from django.shortcuts import render

# Create your views here.
import uuid, json
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.serializers import (
    SendMessageSerializer,
    EditMessageSerializer,
    SuggestionMessageSerializer,
    MyConversationSerializer,
)
from Register.models import UserProfile
# from administration.utils import user_information
from chat.models import ChatMessage
import uuid
from django.utils import timezone
import random
from base.message import suggested_messages
from django.db.models import Q


class SendMessageViewSet(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = SendMessageSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                request_data = serializer.validated_data
                receiver_id = request_data.get("receiver")
                message = request_data.get("message")
                media = request.data.get("media")
                schedule_time = request_data.get("schedule_time")

                forward_id = request_data.get("forward_id")

                if not receiver_id:
                    raise serializers.ValidationError("Receiver ID should be present")

                if not message:
                    raise serializers.ValidationError("Message should be present")

                if forward_id:
                    try:
                        forwarded_message = ChatMessage.objects.get(id=forward_id)
                    except ChatMessage.DoesNotExist:
                        raise serializers.ValidationError("Forwarded message does not exist")

                    message_response = ChatMessage.objects.create(
                        sender=request.user.userprofile,  
                        receiver_id=receiver_id,
                        message=forwarded_message.message,  
                        forwarded_by=request.user.userprofile  
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
                        media=media
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

    # find unread message  after find unread message update read true update & list message
    def list(self, request, *args, **kwargs):
        try:
            # Identify unread messages for the receiver user
            receiver_profile = request.user.userprofile
            unread_messages = ChatMessage.objects.filter(receiver=receiver_profile, is_read=False)

            # Update messages as read
            unread_messages.update(is_read=True)

            # Retrieve conversation messages
            conversation_messages = ChatMessage.objects.filter(Q(sender=request.user.userprofile) | Q(receiver=request.user.userprofile))

            serializer = self.serializer_class(conversation_messages, many=True)
            return Response({"status": True, "message": "Conversation found successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            message = ChatMessage.objects.get(pk=pk)
            if message.sender == request.user.userprofile:
                message.delete()
                return Response({"status": True, "message": "Message deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"status": False, "message": "You don't have permission to delete this message"}, status=status.HTTP_403_FORBIDDEN)
        except ChatMessage.DoesNotExist:
            return Response({"status": False, "message": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditMessageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditMessageSerializer


    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)


            if serializer.is_valid():
                request_data = serializer.validated_data
                message_id = request_data.get("message_id")
                message = request_data.get("message")

                if not message_id:
                    raise serializers.ValidationError("Message ID should be present")

                try:
                    # Retrieve the message to be edited
                    message_to_edit = ChatMessage.objects.get(id=message_id)
                except ChatMessage.DoesNotExist:
                    raise serializers.ValidationError("Message to edit does not exist")

                if request.user.userprofile == message_to_edit.sender:
                    time_elapsed = timezone.now() - message_to_edit.timestamp
                    if time_elapsed.total_seconds() <= 120:  # msg edit only for 2 min
                        message_to_edit.message = message

                        print("new_message::", message)
                        message_to_edit.save()
                        return Response(
                            {"status": True, "message": "Message edited successfully", "data": serializer.data},
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"status": False, "message": "Message can't be edited after 2 minutes"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"status": False, "message": "You are not allowed to edit this message", "data": {}},
                        status=status.HTTP_403_FORBIDDEN,
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


class SuggestMessageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SuggestionMessageSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = serializer.validated_data
                receiver = request.user.userprofile
                print("receiver: ", receiver)
                message_id = request_data.get("message_id")

                try:
                    sender_message = ChatMessage.objects.get(id=message_id)
                except ChatMessage.DoesNotExist:
                    return Response({"error": "Message with the given ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
                
                if sender_message.receiver == receiver:
                    if sender_message.id == int(message_id):
                        sender_message.suggested_message = suggested_messages
                        sender_message.save()

                        return Response(
                            {"status": True, "message": "Suggested message sent successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response({"error": "Permission denied"},status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({"error": "Permission denied. You can only suggest messages where you are the receiver."},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyconversationViewSet(viewsets.ViewSet):
    serializer_class = MyConversationSerializer
    def list(self, request):
        try:
            # Identify unread messages for the receiver user
            receiver_profile = request.user.userprofile
            unread_messages = ChatMessage.objects.filter(receiver=receiver_profile, is_read=False)

            sender_profile = request.user.userprofile
            conversation_messages = ChatMessage.objects.filter(Q(sender=sender_profile))

            if not conversation_messages:
                return Response(
                    {
                        "status": True,
                        "message": "No conversation with any user",
                    },
                    status=status.HTTP_200_OK,
                )

            serializer = self.serializer_class(conversation_messages, many=True)
            return Response({"status": True, "message": "Conversation found successfully", "data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
