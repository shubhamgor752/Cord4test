from django.shortcuts import render
from .models import Post,Comment
from .serializers import createpostSerializer ,ListpostSerializer , CreateCommentSerializer ,LikePostSerializer
from rest_framework.response import Response
from rest_framework import viewsets , status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from Register.models import UserProfile,CustomUser
from rest_framework import serializers
from custom_pagination import CustomPagination

# Create your views here.

class CreatepostView(viewsets.ViewSet,CustomPagination):
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
        

    def list(self,request):
        queryset = Post.objects.filter(author=request.user)

        results = self.paginate_queryset(queryset, request, view=self)

        serializer = ListpostSerializer(results,many=True)
        self.message = 'Post fetched successfully'
        self.res_status = True
        self.data = serializer.data
        self.count = queryset.count()

        return Response({'data': self.data,
                        'message': self.message,
                        'res_status': self.res_status,
                        'code': HttpResponse.status_code})

        # return Response({'status':True,'data':serializer.data,"total_posts":len(serializer.data)},status=status.HTTP_200_OK)        

class ListView(viewsets.ViewSet):
    serializer_class = ListpostSerializer
    def list(self, request):
        queryset = Post.objects.filter(author__is_private=False)
        serializer = ListpostSerializer(queryset, many=True)
        return Response(serializer.data)
    


class CommentView(viewsets.ViewSet):
    serializer_class = CreateCommentSerializer

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)
                print("validated_data:", validated_data)

                post_id = validated_data.get("post_id")
                post = Post.objects.get(pk=post_id)
                print("post=======", post)
                comment = validated_data.get("comment")
                author = request.user
                comment = Comment.objects.create(post=post, comment=comment, author=author)
                return Response(
                        {"status": True, "message": "Comment Created Successfully", "data": serializer.data},
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
        



class LikepostView(viewsets.ViewSet):
    serializer_class = LikePostSerializer

    def create(self,request):
        try:

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)

                post_id = validated_data.get("post_id")

                post = Post.objects.filter(pk=post_id).first()
                user = request.user

                if post.likes.filter(id=user.id).exists():
                    post.likes.remove(user)
                    message = "Post Unliked Successfully"
                else:
                    post.likes.add(user)
                    message = "Post Liked Successfully"
                return Response(
                    {"status": True, "message": message, "data": {}},
                    status=status.HTTP_200_OK,
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
