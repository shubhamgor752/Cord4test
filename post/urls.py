from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CreatepostView,
    PostEditViewSet,
    ListView,
    CommentView,
    LikepostView,
    EventPostViewSet,
    EventeditViewSet,
    JoinEventViewSet,
    PrivateEventViewSet,
    TickerViewSet,
    TicketPurchaseViewSet,
    TickerOderViewSet,
    RemoveFromEventViewSet,
    PollViewSet
)

router = DefaultRouter()
urlpatterns = []

router.register("create/post", CreatepostView, basename='createpost')

router.register("edit/post", PostEditViewSet , basename="edit_post")

router.register("list/post",ListView,basename="list_post")

router.register("comment/add", CommentView,basename="comment") #, "add_a_comment"

router.register("like/send",LikepostView,basename="likes")


router.register("event/create", EventPostViewSet , basename= "event_create")

router.register("edit/event", EventeditViewSet , basename="edit_event")

router.register("join/event",JoinEventViewSet , basename="join_event")

router.register("remove/event", RemoveFromEventViewSet , basename="remove_event")

router.register("private/event", PrivateEventViewSet , basename="private_event")

router.register("ticket/create", TickerViewSet , basename="create_ticket")

router.register("ticker/purchase", TicketPurchaseViewSet , basename="ticket_purchase")

router.register("ticket-order/history", TickerOderViewSet , basename="ticket-history")

router.register("create/poll", PollViewSet , basename="poll-create")



urlpatterns += router.urls
