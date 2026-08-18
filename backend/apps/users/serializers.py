from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User
from .services import CHANNEL_FIELD


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("name", "username", "email", "mob", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SigninSerializer(serializers.Serializer):
    # plain Serializer, not ModelSerializer - we are not creating a row
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # authenticate() checks the hash for us and returns None on failure
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            # same message for wrong password AND unknown user
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


class OTPRequestSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=list(CHANNEL_FIELD))
    value = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=list(CHANNEL_FIELD))
    value = serializers.CharField()
    otp = serializers.CharField()