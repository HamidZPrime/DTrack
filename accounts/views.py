from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from twilio.rest import Client
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .serializers import (
    UserSerializer, UserCreateSerializer, OperatorPermissionSerializer
)
from .models import OperatorPermission, EmailVerificationToken

CustomUser = get_user_model()

class UserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class OperatorPermissionView(generics.ListCreateAPIView):
    queryset = OperatorPermission.objects.all()
    serializer_class = OperatorPermissionSerializer
    permission_classes = [IsAuthenticated]

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            if verification_token.is_valid():
                user = verification_token.user
                user.email_verified = True
                user.save()
                return Response({"detail": _("Email verified successfully.")}, status=status.HTTP_200_OK)
            return Response({"detail": _("Token expired.")}, status=status.HTTP_400_BAD_REQUEST)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": _("Invalid token.")}, status=status.HTTP_404_NOT_FOUND)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class TwoFactorAuthView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        phone_number = request.user.phone_number
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to=phone_number, channel="sms"
        )
        return Response({"detail": _("Verification code sent.")}, status=status.HTTP_200_OK)
