from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CreatepostView,ListView,CommentView,LikepostView

router = DefaultRouter()
urlpatterns = []

router.register("create/post", CreatepostView, basename='createpost')
router.register("list/post",ListView,basename="list_post")
router.register("comment/add", CommentView,basename="comment") #, "add_a_comment"
router.register("like/send",LikepostView,basename="likes")


urlpatterns += router.urls