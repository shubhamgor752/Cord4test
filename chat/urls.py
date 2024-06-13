from rest_framework.routers import DefaultRouter
from chat.views import (
    SendMessageViewSet,
    EditMessageViewSet,
    SuggestMessageViewSet,
    conversationViewSet,
    ScheduledMessageViewSet,
    PendingMsgViewSet,
)

router = DefaultRouter()

urlpatterns = []

router.register("message/send", SendMessageViewSet, basename="send_message")

router.register("message/edit",EditMessageViewSet,basename='edit_message')

router.register("message/suggest",SuggestMessageViewSet,basename='suggest_message')

router.register("list/con", conversationViewSet, basename="list_message")

router.register("pending/message", PendingMsgViewSet , basename="pending_message")

router.register("schedule/messgae", ScheduledMessageViewSet , basename="schedule_message")


urlpatterns += router.urls
