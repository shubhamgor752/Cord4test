from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets , status
from django.http import HttpResponse
from  .models import * 
from group.serializers import (
    GroupSerializer,
    GroupMessagesSerializer,
    AddGroupMemberSerializer,
    JoinRequesGroupSerializer,
    GroupchatSerializer,
    GroupMessageListSerialzers,
)
from django.shortcuts import get_object_or_404
from Register.models import UserProfile,CustomUser
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from custom_pagination import CustomPagination


# Create your views here.


# create grp & member
class GroupViewSet(viewsets.ViewSet):

    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated,]
    res_status, data, message = False, None, 'Invalid request'


    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        group_admin = CustomUser.objects.filter(id=request.user.id).first()
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            group_name = validated_data.get("group_name")
            members = validated_data.get('members', [])
            is_private = validated_data.get("is_private",True)

            existing_group = CustomGroup.objects.filter(group_name=group_name).first()
            if existing_group:
                self.message = 'Group with this name already exists!'
                self.res_status = False
                return Response({'status': self.res_status,
                        'code': HttpResponse.status_code,
                        'message': self.message,
                        'data': self.data})
            
            new_group = CustomGroup.objects.create(group_name=group_name, is_private=is_private)
            new_group.group_admins.add(group_admin)
            
            member_ids = []
            if isinstance(members, list):
                for member_username in members:
                    member = CustomUser.objects.filter(username=member_username).first()
                    if member and member != group_admin:
                        member_ids.append(member.id)
            else:
                member = CustomUser.objects.filter(username=members).first()
                if member and member != group_admin:
                    member_ids.append(member.id)
            
            for member_id in member_ids:
                new_group.members.add(member_id)
            new_group.save()

            self.message = 'Group created successfully!'
            self.res_status = True
            return Response({'status': self.res_status,
                        'code': HttpResponse.status_code,
                        'message': self.message,
                        'data': GroupSerializer(new_group).data})
        else:   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


    # def list(self,request):
        # queryset = Group.objects.filter(group_admins=request.user)

        # serializer = GroupSerializer(queryset,many=True)
        # self.message = 'Group fetched successfully'
        # self.res_status = True
        # self.data = serializer.data
        # self.count = queryset.count()

        # return Response({'data': self.data,
        #                 'message': self.message,
                        # 'res_status': self.res_status,
                        # 'code': HttpResponse.status_code})


    def destroy(self, request, pk=None):
        try:
            group_obj = get_object_or_404(CustomGroup, pk=pk)
        except CustomGroup.DoesNotExist:
            return Response(
                {"status": False, "message": "Group does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        current_user = get_object_or_404(CustomUser, id=request.user.id)

        if current_user not in group_obj.group_admins.all():
            return Response(
                {"status": False, "message": "You are not authorized to delete this group."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            group_obj.delete()
            message = "Successfully deleted the group"
            return Response({'message': message, 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


# edit by only group_admin
class GroupEditViewSet(viewsets.ViewSet):

    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

    message = "Invalid Request"

    def create(self,request, pk=None):
        try:
            pk = request.data.get("id", None)
            group_obj = get_object_or_404(CustomGroup, id=pk)
            current_user = get_object_or_404(CustomUser, id = request.user.id)
            serializer = self.serializer_class(group_obj,data=request.data , partial=True)
            serializer.is_valid(raise_exception = True)

            if group_obj.group_admins.filter(id=current_user.id).exists():

                group_obj = serializer.save()
                print("group_obj==============", group_obj)
                group_obj.save()
                response = GroupMessagesSerializer(group_obj, context={"request": request}).data

                return Response(
                    {"status": True, "message": "group updated", "data": response},
                    status=status.HTTP_201_CREATED,
                )

            else:
                return Response(
                    {"status": False, "message": "You are not authorized to edit this group."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception as e:
            print(e)
            self.message = str(e)

        return Response(
            {"status": False, "message": self.message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

# check list my grp
class MyGroupViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    paginator = CustomPagination()

    message = "INVALID_REQUEST"

    def list(self, request):

        try:
            if not CustomGroup.objects.filter(group_admins=request.user).exists():
                return Response(
                    {"status": False, "message": "You are not authorized to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            queryset = CustomGroup.objects.filter(group_admins=request.user)
            paginated_queryset = self.paginator.paginate_queryset(queryset, request)

            response = GroupMessagesSerializer(paginated_queryset, many=True, context={"request": request}).data

            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "status": True,
                    "message": "My Group list",
                    "data": response,
                }
            )
        except Exception as e:
            print(e)  # Print the actual exception

        return Response(
            {"status": False, "message": self.message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

# remove member from grp & admin remove member
class RemoveMeberViewSet(viewsets.ViewSet):
    res_status , data , message  = False , {} , "Invalid Request"

    def create(self, request):
        try:
            group_id = request.data.get("group_id", None)
            member_id = request.data.get("member_id", None)
            if member_id is None:
                member_id = request.user.id
            current_user_obj = CustomUser.objects.get(id=request.user.id)

            if not CustomGroup.objects.filter(id=group_id).exists():
                return Response(
                    {"status": False, "message": "Invalid group ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not CustomUser.objects.filter(id=member_id).exists():
                return Response(
                    {"status": False, "message": "Invalid user ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            group_obj = get_object_or_404(CustomGroup, id=group_id)

            if (
                member_id != str(current_user_obj.id)
                and group_obj.group_admins.filter(id=current_user_obj.id).exists()
            ):
                user_obj = CustomUser.objects.get(id=member_id)

                if group_obj.members.filter(id=user_obj.id).exists():
                    group_obj.members.remove(user_obj)
# in this case when admin remove member from a group also delete from groupchat table

                    grp_chat_obj = GroupChat.objects.filter(group=group_obj).first()
                    grp_chat_obj.receivers.remove(user_obj)
                    message = f"You removed {user_obj.first_name} from the group"
                else:
                    return Response(
                        {"status": True, "message": "User is not a member of the group"},
                        status=status.HTTP_200_OK,
                    )

            else:
                user_id = str(current_user_obj.id)
                group_obj.members.remove(current_user_obj.id)
                message = "you left the group"

            return Response(
                {"status": True, "message": message},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)

        return Response(
            {"status": False, "message": self.message},
            status=status.HTTP_400_BAD_REQUEST,
        )

# check member in grp only admin access
class GroupMemberViewSet(viewsets.ViewSet):

    permission_classes = (IsAuthenticated,)
    message = "Invalid request"

    def create(self, request, pk=None):
        try:
            group_id = request.data.get("group_id")
            group_obj = get_object_or_404(CustomGroup, id=group_id)
            current_user = get_object_or_404(CustomUser, id = request.user.id)

            if group_obj.group_admins.filter(id=current_user.id).exists():

                # admins = group_obj.group_admins.all()
                # admin_data = [{"id": admin.id, "admin": admin.username} for admin in admins]
                

                members = group_obj.members.all()
                member_data = [{"id": member.id, "name": member.username} for member in members]

                return Response({
                    "status":status.HTTP_200_OK,
                    "message":"Group member found succesfully",
                    "data":member_data
                })

                # response_data = {
                #     # "admins": admin_data,
                #     "members": member_data
                # }

                # return Response(response_data, status=status.HTTP_200_OK)

            else:
                return Response(
                    {
                        "status": False,
                        "message": "You are not authorized to edit this group.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# "After creating the group, additional members can be added to the group."
class AddGrpMemberViewSet(viewsets.ViewSet):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = AddGroupMemberSerializer
    

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            group_id = validated_data.get("group_id")
            members_id = validated_data.get('members_id', [])
            requester_id = request.user.id  # Assuming the user is authenticated

            grp_obj = CustomGroup.objects.filter(id=group_id).first()

            if not grp_obj:
                message = 'Group not found!'
                res_status = False
                return Response({'status': res_status,
                                'code': status.HTTP_404_NOT_FOUND,
                                'message': message})

            if not isinstance(members_id, list):
                members_id = [members_id]

            member_ids = []
            for member_username in members_id:
                member_obj = CustomUser.objects.filter(id=member_username).first()
                
                if not member_obj:
                    message = f'Member with username {member_obj} not found!'
                    res_status = False
                    return Response({'status': res_status,
                                    'code': status.HTTP_404_NOT_FOUND,
                                    'message': message})

                if member_obj in grp_obj.members.all():
                    message = f'Member with username {member_obj} is already in the group.'
                    res_status = False
                    return Response({'status': res_status,
                                    'code': status.HTTP_400_BAD_REQUEST,
                                    'message': message})

                member_ids.append(member_obj.id)
            
            if requester_id != grp_obj.group_admins.first().id:
                message = 'You are not authorized to add members to this group.'
                res_status = False
                return Response({'status': res_status,
                                'code': status.HTTP_403_FORBIDDEN,
                                'message': message})
            
            grp_obj.members.add(*member_ids)

            message = f'Members added to the {grp_obj} successfully.'
            res_status = True
            return Response({'status': res_status,
                            'code': status.HTTP_200_OK,
                            'message': message})

        message = 'Invalid data.'
        res_status = False
        return Response({'status': res_status,
                        'code': status.HTTP_400_BAD_REQUEST,
                        'message': message})


# private Grp Requet send- accept & when group is open join automatic
class AcceptjoinGrpViewSet(viewsets.ViewSet):
    serializer_class = JoinRequesGroupSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                group_id = validated_data.get("group_id")
                is_accept = validated_data.get("is_accept")
                user_id = request.user.id
                grp_obj = CustomGroup.objects.filter(id=group_id).first()
                member = CustomUser.objects.filter(id=user_id).first()

                admin_user = grp_obj.group_admins.filter(id=user_id).first()

                # print("admin_user===============", admin_user)

                if not grp_obj:
                    message = 'Group not found!'
                    res_status = False
                    return Response({'status': res_status,
                                    'code': status.HTTP_404_NOT_FOUND,
                                    'message': message})

                if grp_obj.is_private:
                    member_obj = grp_obj.members.filter(id=user_id).exists()
                    if member_obj:
                        message = f'You are already a member of this {grp_obj} private group!'
                        res_status = False
                        return Response({'status': True,
                                        'code': status.HTTP_200_OK,
                                        'message': message})

                    if is_accept:
                        # IN THIS CASE WHEN USER REQUEST SEND TO PRIVATE GROUP AFTER AGAIN CALL THIS API
                        if admin_user is None:
                            return Response(
                                {"status": False, "message": "You are not authorized to perform this action."},
                                status=status.HTTP_403_FORBIDDEN,
                            )
                        # ========================================== GROUP ADMIN ACCESS================================================================================
                        if user_id==admin_user.id:
                            request_checks = grp_obj.join_requests.all()
                            if request_checks:
                                for request_check in request_checks:
                                    grp_obj.members.add(request_check)
                                grp_obj.join_requests.clear()  # Clear all join requests 
                                res_status = True
                                return Response({'status': res_status,
                                                'code': status.HTTP_200_OK,
                                                'message': f"Request Accepted {request_check}"})
                            else:
                                message = "No pending request found"
                                res_status = False
                                return Response({'status': res_status,
                                                'code': status.HTTP_404_NOT_FOUND,
                                                'message': message})

                        else:
                            message = "Only the group admin can accept join requests."
                            res_status = False
                            return Response({'status': res_status,
                                            'code': status.HTTP_403_FORBIDDEN,
                                            'message': message})
                    else:
                        if admin_user is None:
                            return Response(
                                {"status": False, "message": "You are not authorized to perform this action."},
                                status=status.HTTP_403_FORBIDDEN,
                            )
                        request_check = grp_obj.join_requests.filter(id=user_id).exists()
                        if request_check:
                            jr_obj = grp_obj.join_requests.get(id=user_id)
                            grp_obj.join_requests.remove(jr_obj)
                            message = "Request declined"
                            res_status = True
                            return Response({'status': res_status,
                                            'code': status.HTTP_200_OK,
                                            'message': message})
                        else:
                            if request.user in grp_obj.group_admins.all():
                                return Response(
                                    {
                                        "status": False,
                                        "status": status.HTTP_400_BAD_REQUEST,
                                        "message": "Group admins cannot send join requests to their own group.",
                                    }
                                )
                                # message = "Group admins cannot send join requests to their own group."
                                # res_status = False
                                # return Response({'status': res_status,
                                #                 'code': status.HTTP_404_NOT_FOUND,
                                #                 'message': message})

                            join_request = grp_obj.join_requests.add(user_id)
                            message = 'Your request to join this private group has been sent to the admin.'
                            res_status = True
                            return Response({'status': res_status,
                                            'code': status.HTTP_200_OK,
                                            'message': message})
                else:
                    member_obj = grp_obj.members.filter(id=user_id).exists()
                    if member_obj:
                        message = f'You are already a member of this {grp_obj} group!'
                        res_status = False
                        return Response({'status': res_status,
                                        'code': status.HTTP_403_FORBIDDEN,
                                        'message': message})
                    if admin_user:
                        return Response(
                            {
                                "status": False,
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": "Group admins cannot send join requests to their own group.",
                            }
                        )
                    grp_obj.members.add(user_id)
                    message = f"{member} has joined {grp_obj.group_name}"
                    res_status = True
                    return Response({'status': res_status,
                                    'code': status.HTTP_200_OK,
                                    'message': message})
            message = 'Invalid data!'
            res_status = False
            return Response({'status': res_status,
                            'code': status.HTTP_400_BAD_REQUEST,
                            'message': message})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


class AdminTranserViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        try:
            group_id = request.data.get("group_id", None)
            member_id = request.data.get("member_id", None)
            current_user_obj = CustomUser.objects.get(id=request.user.id)

            if not CustomGroup.objects.filter(id=group_id).exists():
                return Response(
                    {"status": False, "message": "Invalid group ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if not CustomUser.objects.filter(id=member_id).exists():
                return Response(
                    {"status": False, "message": "Invalid user ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            group_obj = get_object_or_404(CustomGroup, id=group_id)

            if not group_obj.group_admins.filter(id=request.user.id):
                return Response(
                {"status": False, "message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

            if group_obj:
                check_member = group_obj.members.filter(id=member_id)
                if check_member:
                    if group_obj.group_admins.filter(id=member_id).exists():
                        message = 'Member is already an admin of this group.'
                        return Response({'status': False, 'message': message})
                    else:
                        group_obj.group_admins.add(member_id)
                        return Response({'status': True, 'message': 'Member added as group admin.'})
                else:
                    message = 'Member ID not in the list of group members.'
                    return Response({'status': False, 'message': message}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccoutSwitch(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    message = "INVALID_REQUEST"

    def create(self, request):
        try:
            group_id = request.data.get("group_id")
            group_obj = get_object_or_404(CustomGroup, id=group_id)
            current_user = request.user

            if group_obj.group_admins.filter(id=current_user.id).exists():
                group_obj.is_private = not group_obj.is_private
                group_obj.save()
                message = (
                    "Switched to public"
                    if not group_obj.is_private
                    else "Switched to private"
                )

                return Response(
                    {
                        "status": True,
                        "message": message,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You are not authorized to edit this group.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GroupMemberCheckViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self,request,*args , **kwargs):
        try:
            group_id = request.data.get("group_id")
            group_obj = get_object_or_404(CustomGroup, id=group_id)
            is_admin = group_obj.group_admins.filter(id=request.user.id).exists()
            is_member = group_obj.members.filter(id=request.user.id).exists()

            if is_admin or is_member:
                serializer = GroupMessagesSerializer(group_obj)
                self.message = 'successfully!'
                self.res_status = True
                return Response({'status': self.res_status,
                            'code': HttpResponse.status_code,
                            'message': self.message,
                            'data': serializer.data})
            else:
                return Response(
                    {
                        "status": False,
                        "message": "You are not in this group",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )



# this api group mesg & save in db this type message = {username}:{message}
# def create(self, request):
#     serializer = self.serializer_class(data=request.data)

#     if serializer.is_valid():
#         validated_data = dict(serializer.validated_data)
#         user = request.user
#         group_id = validated_data.get("group_id")
#         message = validated_data.get("message")
#         # media = request.data.get("media")
#         group_obj = get_object_or_404(CustomGroup, id=group_id)
#         if group_obj.group_admins.filter(id=user.id).exists():
#             group_chat = GroupChat.objects.filter(group=group_obj).first()
#             print("group_chat===========", group_chat)

#             if group_chat:
#                 new_message_content = (
#                     f"{group_chat.message_content}\n{user.username}: {message}"
#                 )
#                 group_chat.message_content = new_message_content
#                 group_chat.save()
#             else:
#                 GroupChat.objects.create(
#                     message_content=f"{user.username}:{message}", group=group_obj
#                 )
#             self.res_status = True
#             self.data = {
#                 "status": self.res_status,
#                 "message": "Message sent successfully",
#             }
#             return Response(self.data, status=status.HTTP_201_CREATED)
#         else:
#             print("33333333333333")
#             self.res_status = False
#             self.data = {
#                 "status": self.res_status,
#                 "message": "You are not a admin of this group",
#             }
#             return Response(self.data, status=status.HTTP_403_FORBIDDEN)
#     else:
#         self.res_status = False
#         self.data = {
#             "status": self.res_status,
#             "message": "Invalid data",
#         }
#         return Response(self.data, status=status.HTTP_403_FORBIDDEN)


# ============================================== group--chat ================================================================

# group-chat in this api only group-admin send message

class GroupchatViewSet(viewsets.ViewSet):
    serializer_class = GroupchatSerializer
    permission_classes = (IsAuthenticated,)
    res_status , data  = False , {}

    def create(self,request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            validated_data = dict(serializer.validated_data)
            user = request.user
            group_id = validated_data.get("group_id")
            message = validated_data.get("message")
            media = request.data.get("media")
            group_obj = get_object_or_404(CustomGroup, id=group_id)
            if group_obj.group_admins.filter(id=user.id).exists():
                group_chat = GroupChat.objects.filter(group=group_obj).first()
                if group_chat:
                    new_message_content = f"{group_chat.message_content},{message}"
                    group_chat.message_content = new_message_content
                    group_chat.save()
                else:
                    GroupChat.objects.create(
                            sender=user, message_content=message, group=group_obj
                        )
                self.res_status = True
                self.data = {'status': self.res_status,'message': 'Message sent successfully'}
                return Response(self.data, status=status.HTTP_201_CREATED)
            else:
                print("33333333333333")
                self.res_status = False
                self.data = {
                    "status": self.res_status,
                    "message": "You are not a admin of this group",
                }
                return Response(self.data, status=status.HTTP_403_FORBIDDEN)
        else:
            self.res_status = False
            self.data = {
                "status": self.res_status,
                "message": "Invalid data",
            }
            return Response(self.data, status=status.HTTP_403_FORBIDDEN)

    # this list-api use for mesg-list , it can use both groupadmin and group-member
    def list(self, request,*args , **kwargs):
        try:
            group_id = request.GET.get("group_id")
            group_obj = get_object_or_404(CustomGroup, id=group_id)
            is_admin = group_obj.group_admins.filter(id=request.user.id).exists()
            is_member = group_obj.members.filter(id=request.user.id).exists()
            if is_admin or is_member:
                chat_obj = GroupChat.objects.filter(group=group_obj)
                serializer = GroupMessageListSerialzers(chat_obj, many=True)
                return Response(
                    {
                        "status": True,
                        "message": "Message list found successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                self.res_status = False
                self.data = {
                    "status": self.res_status,
                    "message": "You are not an admin or a member of this group",
                }
                return Response(self.data, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
