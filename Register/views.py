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
                user_instance = UserProfile.objects.filter(phone_number=mobile_number).first()

                if user_instance:
                    user_token = Token.objects.filter(user=user_instance).first()
                    
                    if not user_token:
                        user_token = Token.objects.create(user=user_instance)

                    
                    message = "Sign-in complete. You're now connected and ready to go."
                    response = {
                        # "mobile_number": mobile_number,
                        "user_token": user_token.key,
                        "user": UserProfileInfo(user_instance).data,
                    }
                else:
                    # user_data = {"mobile_number": mobile_number}
                    user_instance = UserProfile.objects.create(
                        phone_number=mobile_number,
                    )
                    if user_instance != {}:
                        user_token = Token.objects.filter(user=user_instance).first()
                        if not user_token:
                            user_token = Token.objects.create(user=user_instance)
                        # else:
                        #     Token.objects.get(user=user_obj).delete()
                        #     user_token = Token.objects.create(user=user_obj)
                        response = {
                            "user_token": user_token.key,
                            "mobile_number": mobile_number,
                        }
                        message = "Great news! User creation is a success. Get ready to embark on your journey."
                
                self.res_status = True
                self.data = response
                self.message = message
                return Response(
                    {"status": self.res_status, "message": self.message, "data": self.data},
                    status=status.HTTP_201_CREATED,
                )

        return Response(
            {
                "status": self.res_status,
                "code": HttpResponse.status_code,
                "message": self.message,
                # "data": self.data,
            }
        )

class UserViewset(viewsets.ViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
    )  

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
                message = "Username duplicate"
            elif (
                phone_number
                and UserProfile.objects.filter(phone_number=phone_number)
                .exclude(id=instance.id)
                .exclude(is_superuser=True)
                .exists()
            ):
                message = "phone number is already in use"
            elif (
                email
                and UserProfile.objects.filter(email=email)
                .exclude(id=instance.id)
                .exclude(is_superuser=True)
                .exists()
            ):
                message = "email is already in use"
        
            else:
                response = serializer.save(request=request)

                serialized_data = self.serializer_class(response).data

                message = "User update successful"

                return JsonResponse(
                    {"status": True, "message": message, "data": serialized_data},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            message = str(e)
        return JsonResponse(
            {"status": False, "message": message, "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, pk: str = None):
        try:
            user_obj = get_object_or_404(UserProfile, username=pk)
            response = UserProfileInfo(user_obj, context={"request": request}).data
            message = "User Information"
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

class SwitchAccount(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    message = "INVALID_REQUEST"

    def create(self, request):
        try:
            user_instance = get_object_or_404(
                CustomUser, username=request.user.username
            )
            if user_instance.is_private:
                message = "Switched to public"
                user_instance.is_private = False
            else:
                message = "Switched to private"
                user_instance.is_private = True
            user_instance.save()
            return Response(
                {
                    "status": True,
                    "message": message,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            self.message = str(e)

        return Response(
            {"status": False, "message": self.message},
            status=status.HTTP_400_BAD_REQUEST,
        )