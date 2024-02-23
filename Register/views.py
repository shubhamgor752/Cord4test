import re
from .serializers import UserSignUpSerializer
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from Register.models import UserProfile
from Register.serializers import (
    CustomUserSerializer,
    UserProfileInfo,
    USERNAME_VALIDATORS,
    LocationSerializer
)
from django.shortcuts import get_object_or_404
from Register.models import CustomUser
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.core.exceptions import ValidationError


class SignInViewset(viewsets.ViewSet):
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)
    res_status, data, message = False, {}, "Invalid request"

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mobile_number = dict(serializer.validated_data)["mobile_number"]
            otp = (
                dict(serializer.validated_data)["otp"]
                if "otp" in dict(serializer.validated_data).keys()
                else None
            )
            if otp and otp == 1234:
                user_instance = UserProfile.objects.filter(
                    phone_number=mobile_number
                ).first()

                if user_instance:
                    user_token = Token.objects.filter(user=user_instance).first()
                    response = {
                        # "mobile_number": mobile_number,
                        "user_token": user_token.key,
                        "user": UserProfileInfo(user_instance).data,
                    }
                    message = "Sign-in complete. You're now connected and ready to go."

                else:
                    # user_data = {"mobile_number": mobile_number}
                    user_instance = UserProfile.objects.create(
                        phone_number=mobile_number,
                    )
                    if user_instance != {}:
                        user_token = Token.objects.filter(user=user_instance).last()
                        if not user_token:
                            user_token = Token.objects.create(user=user_instance)
                        # else:
                        #     Token.objects.get(user=user_obj).delete()
                        #     user_token = Token.objects.create(user=user_obj)
                        response = {
                            "user_token": user_token.key,
                            "mobile_number": user_instance.username,
                        }
                        message = "Great news! User creation is a success. Get ready to embark on your journey."
                self.res_status, self.data, self.message = (
                    True,
                    response,
                    message,
                )
        return Response(
            {
                "status": self.res_status,
                "code": HttpResponse.status_code,
                "message": self.message,
                "data": self.data,
            }
        )


class UserViewset(viewsets.ViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
    )  # Ensure token authentication is enabled

    def create(self, request):
        try:
            instance = get_object_or_404(CustomUser, id=request.user.id)
            serializer = self.serializer_class(
                instance, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            username = validated_data.get("username")
            phone_number = validated_data.get("phone_number")
            email = validated_data.get("email")
            if (
                username
                and UserProfile.objects.filter(username=username)
                .exclude(id=instance.id)
                .exists()
            ):
                message = "Username already taken"
            elif (
                email
                and UserProfile.objects.filter(email=email)
                .exclude(id=instance.id)
                .exclude(is_superuser=True)
                .exists()
            ):
                message = "Duplicate email address"
            else:
                response = serializer.save(request=request)
                message = "User update successful"
                # Convert CustomUser object to dictionary
                serialized_data = serialize(
                    "json",
                    [
                        response,
                    ],
                )
                response_data = json.loads(serialized_data)[0]["fields"]
                return JsonResponse(
                    {"status": True, "message": message, "data": response_data},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            message = str(e)
        # Debugging statement
        return JsonResponse(
            {"status": False, "message": message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, pk: str = None):
        try:
            user_obj = get_object_or_404(UserProfile, username=pk)
            response = UserProfileInfo(user_obj, context={"request": request}).data
            message = "USER_INFORMATION"
            return Response(
                {"status": True, "message": message, "data": response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            message = str(e)

        return Response(
            {"status": False, "message": message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )


# class UsernameVerification(viewsets.ViewSet):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)
#     def create(self, request):
#         try:
#             username = request.data.get("username", None)
#             errors = []
#             for validator in USERNAME_VALIDATORS:
#                 try:
#                     validator(username)
#                 except ValidationError as e:
#                     errors.extend(e)

#             if errors:
#                 message = ", ".join(errors)
#                 status = False
#             elif CustomUser.objects.filter(username=username).exists():
#                 message = "DUPLICATE_USERNAME"
#                 status = False
#             else:
#                 message = "USERNAME_AVAILABLE"
#                 status = True
#         except Exception as e:
#             message = "INVALID_REQUEST"
#             status = False

#         return Response(
#             {
#                 "status": status,
#                 "code": HttpResponse.status_code,
#                 "message": message,
#             }
#         )


# class SwitchAccount(viewsets.ViewSet):
#     serializer_class = LocationSerializer
#     permission_classes = (IsAuthenticated,)
#     message = "INVALID_REQUEST"

#     def create(self, request):
#         try:
#             user_instance = get_object_or_404(
#                 CustomUser, username=request.user.username
#             )
#             if user_instance.is_private:
#                 message = "Switched to public"
#                 user_instance.is_private = False
#             else:
#                 message = "Switched to private"
#                 user_instance.is_private = True
#             user_instance.save()
#             return Response(
#                 {
#                     "status": True,
#                     "message": message,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as e:
#             self.message = str(e)

#         return Response(
#             {"status": False, "message": self.message},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
