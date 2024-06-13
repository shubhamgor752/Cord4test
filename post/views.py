from django.shortcuts import render
from .models import Post, Comment, EventPost, Ticket ,TicketPurchase
from .serializers import (
    createpostSerializer,
    ListpostSerializer,
    CreateCommentSerializer,
    LikePostSerializer,
    EventPostSerializer,
    JoinEventSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketPurchaseSerializer,
    TickerOrderSerializer,
)
from rest_framework.response import Response
from rest_framework import viewsets , status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from django.http import HttpResponse
from django.shortcuts import get_object_or_404  
from Register.models import UserProfile,CustomUser
from rest_framework import serializers
from custom_pagination import CustomPagination
from connections.models import Connection
from custom_pagination import CustomPagination
from django.db.models import Q , Sum
import json
from django.utils.crypto import get_random_string
from  django.utils import timezone
from rest_framework.pagination import PageNumberPagination
# Create your views here.

class CreatepostView(viewsets.ViewSet,CustomPagination):
    serializer_class = createpostSerializer
    permission_classes = (IsAuthenticated,)
    res_status , data , message = False , {} , "Invalid Request"

    def create(self , request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                request_data = serializer.validated_data
                post_title = request_data.get("post_title")
                description = request_data.get("description")
                print("desc::", description)

                author = request.user
                message_response = Post.objects.create(
                post_title = post_title,
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
        try:
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

        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # return Response({'status':True,'data':serializer.data,"total_posts":len(serializer.data)},status=status.HTTP_200_OK)

    def destroy(self,request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
            if post.author == request.user:
                post.delete()
                return Response({"status": True, "message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"status": False, "message": "You don't have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PostEditViewSet(viewsets.ViewSet):
    serializer_class = createpostSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, pk=None):
        try:
            post_id = request.data.get("id", None)
            post_obj = get_object_or_404(Post, id=post_id)
            current_user = request.user

            if post_obj.author != current_user:
                return Response(
                    {
                        "status": False,
                        "message": "You are not authorized to edit this post.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = self.serializer_class(
                post_obj, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            post_obj = serializer.save()
            response_data = createpostSerializer(
                post_obj, context={"request": request}
            ).data
            return Response(
                {"status": True, "message": "Post updated", "data": response_data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response(
                {"status": False, "message": error_message, "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ListView(viewsets.ViewSet):
    serializer_class = ListpostSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        try:
            current_user = request.user
            user_connection = Connection.objects.get(user=current_user)
            follower_list = user_connection.followers.all()
            # print("follower_list======",follower_list)
            queryset = Post.objects.filter(author__in=follower_list)
        except Connection.DoesNotExist:
            queryset = Post.objects.none()  # If the user's connection doesn't exist, return an empty queryset

        serializer = ListpostSerializer(queryset, many=True)
        return Response(serializer.data)


class CommentView(viewsets.ViewSet):
    serializer_class = CreateCommentSerializer

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)
                post_id = validated_data.get("post_id")
                comment = validated_data.get("comment")
                post = Post.objects.get(pk=post_id)
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

    def destroy(self, request , pk = None):
        try:
            comment = Comment.objects.get(pk=pk)
            if comment.author == request.user:
                comment.delete()
                return Response({"message":"Comment delete succesfully"})

            else:
                return Response({"message":"You are not authorized to delete this comment"})

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


class EventPostViewSet(viewsets.ViewSet,CustomPagination):
    serializer_class = EventPostSerializer
    permission_classes = (IsAuthenticated,)
    res_status , data , message = False , {} , "Invalid Request"

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)
                author = request.user
                description = validated_data.get("description")
                title = validated_data.get("title")
                event_type = validated_data.get("event_type")
                event_date = validated_data.get("event_date")
                event_end_date = validated_data.get("event_end_date")
                event_location = validated_data.get("event_location")
                ticket_price = validated_data.get("ticket_price")

                if EventPost.objects.filter(title=title).exists():
                    return Response({"message": "Event already exists"}, status=status.HTTP_400_BAD_REQUEST)

                message_response = EventPost.objects.create(
                    description=description, 
                    author=author,
                    title = title,
                    event_type = event_type,
                    event_date = event_date,
                    event_end_date = event_end_date,
                    event_location = event_location,
                    ticket_price = ticket_price,
                    )
                return Response(
                    {
                        "status": True,
                        "message": "Event Create Successfully",
                        "data": serializer.data,
                    },
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

    def list(self, request):
        try:
            event_location = request.GET.get("event_location")
            event_type = request.GET.get("event_type")
            # print("event_type===================", event_type)

            # Filter the events by the author and optionally by event_location
            queryset = EventPost.objects.filter(author=request.user)
            if event_location:
                queryset = queryset.filter(event_location__icontains=event_location)
                

            if event_type:
                queryset = queryset.filter(event_type__icontains=event_type)
                

            if queryset.exists():
                result = self.paginate_queryset(queryset, request, view=self)
                serializer = self.serializer_class(result, many=True)

                self.message = "Events fetched successfully"
                self.res_status = True
                self.data = serializer.data

                return self.get_paginated_response(
                    {
                        "data": self.data,
                        "message": self.message,
                        "res_status": self.res_status,
                        "code": HttpResponse.status_code,
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "No events found for the specified criteria",
                    }
                )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request , pk=None):
        try:
            event = EventPost.objects.get(pk=pk)
            if event.author == request.user:
                event.delete()
                return Response({
                    "status":True,
                    "message":"Event Delete Succesfully"
                })
            else:
                return Response({
                    "status":False,
                    "message":"you can't delete this post"
                })
        except Exception as e:
            return Response({
                "status":False,
                "message":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
            )


class EventeditViewSet(viewsets.ViewSet):
    serializer_class = EventPostSerializer
    permission_classes = (IsAuthenticated,)

    def create(self,request, pk=None):
        try:
            pk = request.data.get("event_id", None)
            event_obj = get_object_or_404(EventPost , id=pk)
            current_user = request.user
            serializer = self.serializer_class(event_obj , data=request.data , partial=True)
            if serializer.is_valid(raise_exception=True):
                if event_obj.author == current_user:
                    event_obj = serializer.save()
                    event_obj.save()
                    response_data = EventPostSerializer(event_obj , context={"request":request}).data
                    return Response({
                        "status": True,
                        "message": "Event Updated Successfully",
                        "data":response_data
                    })
                else:
                    return Response({
                        "status":False,
                        "message":"You can't edit this event"
                    })
        except Exception as e:
            return Response({"status":False, "message":str(e), "data":{}},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JoinEventViewSet(viewsets.ViewSet):
    serializer_class = JoinEventSerializer
    permission_classes = (IsAuthenticated,)

    res_status, data, message = False, {}, "Invalid Request"

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                validated_data = serializer.validated_data
                event_id = validated_data.get("event_id")

                user = request.user
                event_post = EventPost.objects.get(pk=event_id)

                if user == event_post.author:
                    return Response(
                        {"message": "You are group event author."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if event_post.event_type != EventPost.FREE:
                    return Response(
                        {"message": "This event is not free."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                event_post.joining_users.add(request.user)
                return Response(
                    {"message": "You have joined the event."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except EventPost.DoesNotExist:
            return Response(
                {"message": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemoveFromEventViewSet(viewsets.ViewSet):
    # serializer_class = JoinEventSerializer
    permission_classes = (IsAuthenticated,)

    def create(self,request):
        try:
            event_id = request.data.get("event_id", None)
            current_user_obj = get_object_or_404(CustomUser , id=request.user.id)
            event_obj = get_object_or_404(EventPost, id=event_id)
            if event_obj.event_type != "paid":
                if event_obj.author != current_user_obj:
                    event_obj.joining_users.remove(current_user_obj.id)
                    return Response({
                        "status":True,
                        "message": f"You are leave for this {event_obj.title}"
                    })
                else:
                    return Response({
                        "status":False,
                        "message":"you are group author"
                    })
            else:
                return Response({"status": False, "message": "Event is paid"})
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================================pendingggg===================================
class PrivateEventViewSet(viewsets.ViewSet):
    serializer_class = JoinEventSerializer
    permission_classes = (IsAuthenticated,)

    res_status , data , message = False , {} , "Invalid Request"

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                event_id = validated_data.get("event_id")
                user = request.user
                try:
                    event_post = EventPost.objects.get(pk=event_id)
                except EventPost.DoesNotExist:
                    return Response(
                        {"message": "Event does not exist."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if event_post.event_type != EventPost.PAID:
                    return Response(
                        {"message": "This event is not paid."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if user == event_post.author:
                    return Response(
                        {"message": "You are group event author."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                try:
                    ticket = Ticket.objects.get(event=event_post)
                except Ticket.DoesNotExist:
                    return Response(
                        {"message": "Tickets for this event are not available."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if ticket.available_quantity <= 0:
                    return Response(
                        {"message": "No tickets available for this event."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    if event_post.joining_users.filter(id=request.user.id).exists():
                        return Response({'message':'User already join in this private event'})
                    else:
                        event_post.joining_users.add(request.user)
                        ticket.available_quantity -= 1
                        ticket.save()
                        return Response(
                            {
                                "message": "Ticket purchased successfully.",
                                # "data": json.loads(user),
                            },
                            status=status.HTTP_200_OK,
                        )
            else: 
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except EventPost.DoesNotExist:
            return Response(
                {"message": "Event does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TickerViewSet(viewsets.ViewSet):

    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    res_status , data , message = False , {} , "Invalid Request"

    # @staticmethod
    # def get_ticket(request):
    #     return Ticket.objects.filter(id=request.user.id).first()

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)
                event_id = validated_data.get("event_id")
                ticket_price = validated_data.get("ticket_price")
                available_quantity = validated_data.get("available_quantity")

                event_post = get_object_or_404(EventPost, id=event_id)
                print(event_post.event_type)

                if event_post.author != request.user:
                    return Response(
                        {"message": "You are not the author of this event."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if not event_post.event_type == "paid":
                    return Response(
                        {"message": "Cannot create ticket for a free event."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if Ticket.objects.filter(event_id=event_id).exists():
                    return Response({"message":"Ticket already created for this event"})

                Ticket.objects.create(
                    event_id=event_id,
                    ticket_price=ticket_price,
                    available_quantity=available_quantity,
                    author=request.user,
                )
                return Response(
                    {
                        "status": True,
                        "message": "Ticket created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Invalid data", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # def list(self, request, event_id=None):
    #     try:
    #         event_id = request.data.get("event_id")
    #         event_post = get_object_or_404(EventPost, id=event_id)
    #         print("event_post=======", event_post)

    #         if event_post.author != request.user:
    #             return Response(
    #                 {"message": "You are not the author of this event."},
    #                 status=status.HTTP_403_FORBIDDEN,
    #             )

    #         tickets = Ticket.objects.filter(event=event_post)
    #         serializer = self.serializer_class(tickets, many=True)

    #         return Response(
    #             {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
    #         )
    #     except Exception as e:
    #         return Response(
    #             {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    def list(self, request):
        try:
            # Filter tickets based on the author or associated event's author

            tickets = Ticket.objects.filter(Q(author=request.user) | Q(event__author=request.user))
            if not tickets:
                return Response(
                    {
                        "status": False,
                        "message": "Onlt admin can access this request",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            serializer = TicketListSerializer(tickets, many=True)

            return Response(
                {
                    "status": True,
                    "message": "Tickets fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        try:
            ticket_instance = get_object_or_404(Ticket, pk=pk)

            serializer = self.serializer_class(
                ticket_instance, data=request.data, partial=True
            )

            if serializer.is_valid():
                validated_data = serializer.validated_data

                # Update fields if provided, otherwise keep existing
                ticket_instance.ticket_price = validated_data.get(
                    "ticket_price", ticket_instance.ticket_price
                )
                ticket_instance.available_quantity = validated_data.get(
                    "available_quantity", ticket_instance.available_quantity
                )

                # Save the updated ticket instance
                ticket_instance.save()
                return Response(
                    {
                        "status": True,
                        "code": status.HTTP_200_OK,
                        "message": "Ticket updated successfully",
                    }
                )
                # return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response ({
                        "status": False,
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Validation error",
                        "errors": serializer.errors
                    })
                # return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "Ticket not found",
                }
            )
            # return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": str(e),
                }
            )
            # return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketPurchaseViewSet(viewsets.ViewSet):

    serializer_class = TicketPurchaseSerializer
    permission_classes = (IsAuthenticated,)

    def create(self,request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = dict(serializer.validated_data)
                ticket = validated_data.get("ticket")
                quantity = validated_data.get("quantity")
                ticket_obj = get_object_or_404(Ticket, id=ticket.id)

                event = ticket_obj.event

                if ticket_obj.author == request.user:
                    return Response({"message": "You are the ticket authorizer;"})  

                if ticket_obj.available_quantity < quantity:
                    return Response(
                        {"message": "Not enough tickets available."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if event.event_end_date < timezone.now().date():
                    # ticket_obj.delete()   Automatically delete this event when it ends, when second time call this API
                    return Response(
                        {"message": "The event is closed."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user_purchases = TicketPurchase.objects.filter(
                    user=request.user, ticket=ticket_obj
                )
                if user_purchases.exists():
                    return Response(
                        {
                            "message": "You have already purchased a ticket for this event. No additional tickets can be booked."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                total_tickets_booked = (
                    user_purchases.aggregate(total=Sum("quantity"))["total"] or 0
                )
                if total_tickets_booked + quantity > 5:
                    return Response(
                        {
                            "message": "You can only book a maximum of 8 tickets for this event."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                ticket_obj.available_quantity -= quantity
                ticket_obj.save()

                order_id = get_random_string(length=32)
                TicketPurchase.objects.create(
                    ticket=ticket_obj,
                    user=request.user,
                    quantity=quantity,
                    order_id=order_id
                )
                event = ticket_obj.event
                if event.event_type == 'paid':
                    event.joining_users.add(request.user)
                    event.save()
                return Response(
                    {
                        "status": True,
                        "message": "Ticket purchased successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Invalid data", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
#  for ticket cancel
    def destroy(self,request, pk=None):
        try:

            purchase_obj = TicketPurchase.objects.get(pk=pk)

            if purchase_obj.user == request.user:
                ticket = purchase_obj.ticket
                event = ticket.event

                if event.event_end_date < timezone.now().date():
                    return Response({
                        "message":"The event is closed"
                    }, status=status.HTTP_400_BAD_REQUEST)

                ticket.available_quantity += purchase_obj.quantity
                ticket.save()
                purchase_obj.delete()

                if event.event_type == 'paid':
                    event.joining_users.remove(request.user)

                    return Response({
                        "status":True , "message":"Ticket cancelled succssfully"
                    }, status= status.HTTP_200_OK)

            else:
                return Response(
                    {
                        "status": False,
                        "message": "You are not authorized for this request",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TickerOderViewSet(viewsets.ViewSet, CustomPagination):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        try:
            queryset = TicketPurchase.objects.filter(user=request.user)
            if not queryset.exists():
                return Response(
                    {"message": "You have no orders yet.", "orders": []},
                    status=status.HTTP_200_OK,
                )

            result = self.paginate_queryset(queryset , request , view=self)
            serializer = TickerOrderSerializer(result, many=True)
            serialized_data = serializer.data

            self.message = 'Order fetched successfully'
            self.res_status = True
            self.data = serializer.data

            return self.get_paginated_response(
                {   'data': self.data,
                    'message': self.message,
                    'res_status': self.res_status,
                    'code': HttpResponse.status_code
                }
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
