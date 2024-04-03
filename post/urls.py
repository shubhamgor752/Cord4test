from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreatepostView,ListView

router = DefaultRouter()
urlpatterns = []

router.register("create/post", CreatepostView, basename='createpost')
router.register("list/post",ListView,basename="list_post")


urlpatterns += router.urls