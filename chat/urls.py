from rest_framework.routers import DefaultRouter
from chat.views import (
    SendMessageViewSet,
    EditMessageViewSet,
    SuggestMessageViewSet,
    MyconversationViewSet,
)

router = DefaultRouter()

urlpatterns = []

router.register("message/send", SendMessageViewSet, basename="send_message")
router.register("message/edit",EditMessageViewSet,basename='edit_message')

router.register("message/suggest",SuggestMessageViewSet,basename='suggest_message')

router.register("my/con", MyconversationViewSet, basename="my_message")


urlpatterns += router.urls
