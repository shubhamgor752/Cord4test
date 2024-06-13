from .views import SignInViewset, UserViewset, SwitchAccount, UserListViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("signin", SignInViewset, basename="signin")

router.register("user", UserViewset, basename="user")  # edit user/business profile

# router.register("username/verification", UsernameVerification, basename="username_verification")

router.register("switch-account", SwitchAccount, basename="switch_account")


router.register("users/list", UserListViewSet, basename="user_list")


urlpatterns = router.urls
