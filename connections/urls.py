from rest_framework.routers import DefaultRouter
from connections.views import FollowRequestView , AcceptFollowRequestView , FollowbackView
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path("acceptfollowrequest", AcceptFollowRequestView.as_view())

]

router.register("follow/send", FollowRequestView, basename="send_follow")
router.register("follow/back", FollowbackView, basename="followback")






urlpatterns += router.urls
