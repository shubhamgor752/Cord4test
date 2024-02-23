from rest_framework.routers import DefaultRouter
from chat.views import SendMessageViewSet

router = DefaultRouter()

urlpatterns = []

router.register("message/send", SendMessageViewSet, basename="send_message")

urlpatterns += router.urls
