from .views import SignInViewset, UserViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("signin", SignInViewset, basename="signin")
router.register("user", UserViewset, basename="user")  # edit user/business profile

# router.register("username/verification", UsernameVerification, basename="username_verification")

# router.register("switch-account", SwitchAccount, basename="switch_account")



urlpatterns = router.urls
