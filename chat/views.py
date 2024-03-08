from django.shortcuts import render

# Create your views here.
import uuid, json
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.serializers import (
    SendMessageSerializer , EditMessageSerializer
)
from Register.models import UserProfile
# from administration.utils import user_information
from chat.models import ChatMessage
import uuid
from django.utils import timezone




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
          
    def list(self, request, *args, **kwargs):
        try:
            conversation_messages = ChatMessage.objects.filter(sender=request.user.userprofile)
            # print("conversation_messages=======",conversation_messages )
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
                    print("message_to_edit:", message_to_edit)
                except ChatMessage.DoesNotExist:
                    raise serializers.ValidationError("Message to edit does not exist")

                if request.user.userprofile == message_to_edit.sender:
                    time_elapsed = timezone.now() - message_to_edit.timestamp
                    if time_elapsed.total_seconds() <= 1200:  # msg edit only for 2 min
                        message_to_edit.message = message

                        print("new_message::", message)
                        message_to_edit.save()
                        return Response(
                            {"status": True, "message": "Message edited successfully", "data": serializer.data},
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"status": False, "message": "Message can't be edited after 2 minutes", "data": {}},
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