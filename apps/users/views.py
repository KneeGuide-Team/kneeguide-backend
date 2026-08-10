import random
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (
    EmailSerializer,
    LoginSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)
from .models import User, EmailOTP
from .services.email import send_otp_email


def generate_otp():
    return str(random.randint(100000, 999999))


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Auto-assign doctor
            doctor = User.objects.filter(role='doctor', is_available=True).first()
            if doctor:
                user.assigned_doctor = doctor
                user.save(update_fields=["assigned_doctor"])

            # Create OTP
            code = generate_otp()
            EmailOTP.objects.create(user=user, code=code)

            send_otp_email(user.email, code)

            return Response({"message": "OTP sent to email"}, status=201)

        return Response(serializer.errors, status=400)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    MAX_ATTEMPTS = 5

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email__iexact=email)
                otp = EmailOTP.objects.filter(user=user, verified=False).last()

                if not otp:
                    return Response({"error": "No OTP found"}, status=404)

                # expiration check
                if otp.is_expired():
                    return Response({"error": "OTP expired"}, status=400)

                # attempts limit
                if otp.attempts >= self.MAX_ATTEMPTS:
                    return Response(
                        {"error": "Too many attempts. Request new code."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

                # wrong code
                if otp.code != code:
                    otp.attempts += 1
                    otp.save(update_fields=["attempts"])
                    return Response({"error": "Invalid OTP"}, status=400)

                # success
                otp.verified = True
                otp.save(update_fields=["verified"])

                user.is_active = True
                user.save(update_fields=["is_active"])

                return Response({"message": "OTP verified"}, status=200)

            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        return Response(serializer.errors, status=400)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # prevent spam (3 OTP per 10 minutes)
        ten_min_ago = timezone.now() - timedelta(minutes=10)
        recent_otps = EmailOTP.objects.filter(user=user, created_at__gte=ten_min_ago)

        if recent_otps.count() >= 3:
            return Response(
                {"error": "Too many OTP requests. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        code = generate_otp()
        EmailOTP.objects.create(user=user, code=code)
        send_otp_email(user.email, code)

        return Response({"message": "OTP resent"}, status=200)


class LoginView(APIView):
    """
    تسجيل الدخول باستخدام الإيميل والباسورد
    يرجع Access Token فقط لمدة 5 دقائق
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        matched_user = User.objects.filter(email__iexact=email).first()
        authentication_email = matched_user.email if matched_user else email

        user = authenticate(username=authentication_email, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        if not user.is_active:
            return Response({"error": "Account not verified yet."}, status=403)

        # إنشاء access token فقط
        access = AccessToken.for_user(user)

        return Response({
            "access": str(access),
            "expires_in_minutes": 5,
            "user": {
                "id": user.id,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }, status=200)


class MeView(APIView):
    """
    Endpoint بسيط يرجع بيانات المستخدم الحالي (مفيد للفرونت)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']

        exists = User.objects.filter(email__iexact=email).exists()
        return Response({"exists": exists})
