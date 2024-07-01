from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GroupViewSet,
    RemoveMeberViewSet,
    MyGroupViewSet,
    GroupMemberViewSet,
    GroupEditViewSet,
    AddGrpMemberViewSet,
    AcceptjoinGrpViewSet,
    AdminTranserViewSet,
    AccoutSwitch,
    GroupchatViewSet,
    GroupMemberCheckViewSet
)

router = DefaultRouter()

urlpatterns = []

router.register('create/group', GroupViewSet ,basename='groupname')
router.register('add/member', AddGrpMemberViewSet, basename='addmember')
router.register('my/group',MyGroupViewSet,basename= 'mygroups')
router.register('group/edit',GroupEditViewSet,basename='groupedit')
router.register('group/member',GroupMemberViewSet, basename='groupdetail') #,'remove_member_viewset')
router.register('remove/member', RemoveMeberViewSet, basename='removemember')
router.register('request/group',AcceptjoinGrpViewSet, basename='acceptjoingrp')

router.register('another/admin', AdminTranserViewSet , basename='admincreate')

router.register('private/public', AccoutSwitch , basename='accountswitch' )

router.register('group/chat', GroupchatViewSet, basename='groupchat')

router.register("check/group-member", GroupMemberCheckViewSet , basename="check-member")


urlpatterns += router.urls
