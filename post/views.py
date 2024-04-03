from django.shortcuts import render
from .models import Post
from .serializers import createpostSerializer ,ListpostSerializer
from rest_framework.response import Response
from rest_framework import viewsets , status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from Register.models import UserProfile,CustomUser
from rest_framework import serializers
# Create your views here.

class CreatepostView(viewsets.ViewSet):
    serializer_class = createpostSerializer
    # permission_classes = (IsAuthenticated,)
    res_status , data , message = False , {} , "Invalid Request"

    def create(self , request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = serializer.validated_data
                description = request_data.get("description")
                print("desc::", description)

                author = request.user
                message_response = Post.objects.create(
                description = description,
                author=author

                )
                return Response(
                        {"status": True, "message": "Post Create Successfully", "data": serializer.data},
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
        

class ListView(viewsets.ViewSet):
    serializer_class = ListpostSerializer
    def list(self, request):
        queryset = Post.objects.filter(author__is_private=False)
        serializer = ListpostSerializer(queryset, many=True)
        return Response(serializer.data)