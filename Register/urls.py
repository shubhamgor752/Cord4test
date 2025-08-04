from .views import SignInViewset, UserViewset, SwitchAccount, UserListViewSet,LogoutViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("signin", SignInViewset, basename="signin")

router.register("user", UserViewset, basename="user")  # edit user/business profile

# router.register("username/verification", UsernameVerification, basename="username_verification")

router.register("switch-account", SwitchAccount, basename="switch_account")


router.register("users/list", UserListViewSet, basename="user_list")


router.register("logout", LogoutViewset, basename='logout')



urlpatterns = router.urls
