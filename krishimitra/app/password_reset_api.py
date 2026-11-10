import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import PasswordResetOTP

logger = logging.getLogger(__name__)

OTP_LIFETIME = timedelta(minutes=5)
RESEND_COOLDOWN = timedelta(seconds=60)
MAX_ATTEMPTS = 5


class PublicAuthView(APIView):
    """Endpoints used while logged OUT.
    - authentication_classes = [] : a stale/expired token in the browser must not cause a 401
    - throttled per IP (rate set in settings: DEFAULT_THROTTLE_RATES["password_reset"])
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(r"^\d{6}$", error_messages={"invalid": "Enter the 6-digit code."})


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "The two passwords don't match."})
        return attrs


def can_reset(user):
    profile = getattr(user, "profile", None)
    return user.is_active and (profile is None or profile.is_active_account)


class ForgotPasswordView(PublicAuthView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email__iexact=email).first()
        if user and can_reset(user):
            record = PasswordResetOTP.objects.filter(user=user).first()
            recently_sent = record and timezone.now() - record.issued_at < RESEND_COOLDOWN
            if not recently_sent:
                code = f"{secrets.randbelow(1_000_000):06d}"     
                PasswordResetOTP.objects.update_or_create(
                    user=user,
                    defaults={"code_hash": make_password(code), "issued_at": timezone.now(), "attempts": 0},
                )
                try:
                    send_mail(
                        subject="KrishiMitra OTP Verification",
                        message=(
                            f"Hi {user.first_name or user.username},\n\n"
                            f"Your OTP for password reset is:\n\n{code}\n\n"
                            f"This OTP expires in 5 minutes. If you didn't ask for it, ignore this email."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )
                except Exception:
                    logger.exception("Could not send reset OTP email")

        # same answer whether or not the email exists, so this can't be used to find registered emails
        return Response({"detail": "If that email is registered, we've sent a 6-digit code to it."})


class VerifyOTPView(PublicAuthView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        bad = Response({"detail": "Invalid or expired code. Please request a new one."},
                       status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()
        record = PasswordResetOTP.objects.filter(user=user).first() if user else None
        if record is None:
            return bad

        expired = timezone.now() - record.issued_at > OTP_LIFETIME
        if expired or record.attempts >= MAX_ATTEMPTS:
            record.delete()                                       
            return bad

        if not check_password(otp, record.code_hash):
            PasswordResetOTP.objects.filter(pk=record.pk).update(attempts=F("attempts") + 1)
            return bad

        record.delete()                                          
        return Response({
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),    
        })


class ResetPasswordView(PublicAuthView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(data["uid"])))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not can_reset(user) or not default_token_generator.check_token(user, data["token"]):
            return Response({"detail": "This reset session has expired. Please start again."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            password_validation.validate_password(data["new_password1"], user)
        except DjangoValidationError as exc:
            return Response({"new_password1": list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data["new_password1"])
        user.save()      
        return Response({"detail": "Password reset successful."})
