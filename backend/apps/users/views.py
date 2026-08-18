from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    SigninSerializer,
    SignupSerializer,
)
from .services import create_otp, find_user, send_otp, verify_otp


def issue_token(user):
    """The single place a token is created - all three methods end here."""
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, "username": user.username}


class SignupView(APIView):
    """Create a new account."""

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(issue_token(user), status=status.HTTP_201_CREATED)


class SigninView(APIView):
    """Method 1: username + password."""

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(issue_token(serializer.validated_data["user"]))


class OTPRequestView(APIView):
    """Methods 2 and 3, step 1: send a code to mobile or email."""

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.validated_data["channel"]
        value = serializer.validated_data["value"]

        user = find_user(channel, value)
        if user is not None:
            code = create_otp(channel, value)
            send_otp(channel, value, code)

        # identical response either way, so nobody can discover who is registered
        return Response({"detail": "If the account exists, a code has been sent."})


class OTPVerifyView(APIView):
    """Methods 2 and 3, step 2: exchange the code for a token."""

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.validated_data["channel"]
        value = serializer.validated_data["value"]

        if not verify_otp(channel, value, serializer.validated_data["otp"]):
            return Response({"detail": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)

        user = find_user(channel, value)
        if user is None:
            return Response({"detail": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(issue_token(user))