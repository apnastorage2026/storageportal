import re

from rest_framework import serializers
from .models import User

ALLOWED_EMAIL_DOMAIN = "gmail.com"
MOB_PATTERN = re.compile(r"^[6-9]\d{9}$")   # Indian mobile: starts 6-9, exactly 10 digits


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "username", "email", "mob", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    # DRF finds this by name and calls it for the "email" field
    def validate_email(self, value):
        # split on the last "@" so "a@b@gmail.com" can't sneak through
        domain = value.rsplit("@", 1)[-1].lower()
        if domain != ALLOWED_EMAIL_DOMAIN:
            raise serializers.ValidationError(f"Only {ALLOWED_EMAIL_DOMAIN} addresses are allowed.")
        return value.lower()   # whatever you return is what gets saved

    def validate_mob(self, value):
        if not MOB_PATTERN.fullmatch(value):
            raise serializers.ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)