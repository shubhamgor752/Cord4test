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
    LocationSerializer,
    SetPinSerializer
)
from django.shortcuts import get_object_or_404
from Register.models import CustomUser
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.core.exceptions import ValidationError
from custom_pagination import CustomPagination, CustomPaginationnnnn
from .models import UserProfile, OTPRequest
from .utils import generate_otp, send_otp_via_twilio
from django.contrib.auth.hashers import make_password , check_password


class SignInViewset(viewsets.ViewSet):
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)
    res_status, data, message = False, {}, "Invalid request"

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data["mobile_number"]
            otp = serializer.validated_data.get("otp")
            pin = serializer.validated_data.get("pin")


            user_instance = UserProfile.objects.filter(phone_number=mobile_number).first()


            if pin and user_instance and user_instance.pin:
                if check_password(pin, user_instance.pin):
                    token, _ = Token.objects.get_or_create(user=user_instance)
                    return Response({
                        "status": True,
                        "message": "Sign-in complete. You're now connected and ready to go.",
                        "data": {
                            "user_token": token.key,
                            "user": UserProfileInfo(user_instance).data,
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "status": False,
                        "message": "Invalid PIN.",
                    }, status=status.HTTP_401_UNAUTHORIZED)

            #  If user has PIN but no PIN sent → force PIN login
            if user_instance and user_instance.pin and not pin and not otp:
                return Response({
                    "status": False,
                    "message": "PIN already set. Please login using your PIN.",
                }, status=status.HTTP_403_FORBIDDEN)

            if not otp:
                # Step 1: Send OTP using Twilio
                generated_otp = generate_otp()
                OTPRequest.objects.create(mobile_number=mobile_number, otp=generated_otp)
                send_otp_via_twilio(mobile_number, generated_otp)

                return Response({
                    "status": True,
                    "message": "OTP has been sent to your mobile number."
                }, status=status.HTTP_200_OK)

            # Step 2: Verify OTP
            otp_instance = OTPRequest.objects.filter(mobile_number=mobile_number, otp=otp).order_by("-created_at").first()
            if not otp_instance or otp_instance.is_expired():
                return Response({"message": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

            # Step 3: Proceed with user login or registration
            user_instance = UserProfile.objects.filter(phone_number=mobile_number).first()

            if user_instance:
                user_token = Token.objects.get_or_create(user=user_instance)[0]
                response = {
                    "user_token": user_token.key,
                    "user": UserProfileInfo(user_instance).data,
                }
                message = "Sign-in complete. You're now connected and ready to go."
            else:
                user_instance = UserProfile.objects.create(
                    phone_number=mobile_number,
                    is_superuser=True,
                )
                user_token = Token.objects.create(user=user_instance)
                response = {
                    "user_token": user_token.key,
                    "mobile_number": mobile_number,
                }
                message = "Great news! User creation is a success."

            self.res_status = True
            self.data = response
            self.message = message

            return Response({
                "status": self.res_status,
                "message": self.message,
                "data": self.data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": self.res_status,
            "message": self.message,
        }, status=status.HTTP_400_BAD_REQUEST)

class SetPinViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = SetPinSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data['pin']
            user = request.user

            if user.pin:
                return Response({
                    "status": False,
                    "message": "PIN already set. You cannot reset it here.",
                }, status=status.HTTP_400_BAD_REQUEST)

            user.pin = make_password(pin)
            user.save()

            return Response({
                "status": True,
                "message": "PIN set successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
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

            username = validated_data["username"].replace(" ", "_").lower()
            validated_data["username"] = username
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
            user_obj = get_object_or_404(UserProfile, id=request.user.id)
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


class UserListViewSet(viewsets.ViewSet, CustomPagination):

    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        try:
            user_status = request.user.is_superuser
            if user_status == True:
                queryset = UserProfile.objects.all()
                result = self.paginate_queryset(queryset, request, view=self)
                serializer = self.serializer_class(result, many=True)
                serialize_data = serializer.data

                return self.get_paginated_response(
                    {
                        "data": serialize_data,
                        "message": "User List",
                        "res_status": status.HTTP_200_OK,
                        "code": HttpResponse.status_code,
                    }
                )

            else:
                return Response({"messgae": "Access denied for user"})
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )





class LogoutViewset(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):  # POST /logout/
        user = request.user

        # Check if token exists for the user
        token_qs = Token.objects.filter(user=user)
        if not token_qs.exists():
            # Token already deleted (probably on previous logout)
            return Response({
                "status": False,
                "message": "Please login first."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Delete token (first-time logout)
        token_qs.delete()

        return Response({
            "status": True,
            "message": "You have been successfully logged out. Token has been deleted."
        }, status=status.HTTP_200_OK)