import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone

from .models import OTP, User

# maps the channel name to the User field that stores it
CHANNEL_FIELD = {"mobile": "mob", "email": "email"}


def find_user(channel, value):
    """Look up a user by mobile or email. Returns None if not found."""
    return User.objects.filter(**{CHANNEL_FIELD[channel]: value}).first()


def create_otp(channel, value):
    """Generate a code, store only its hash, return the raw code for sending."""
    digits = "0123456789"
    # secrets, not random - random is predictable and unsafe for codes
    code = "".join(secrets.choice(digits) for _ in range(settings.OTP_LENGTH))

    OTP.objects.create(
        channel=channel,
        value=value,
        code_hash=make_password(code),
        expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
    )
    return code


def send_otp(channel, value, code):
    """Deliver the code. Swap these bodies for a real provider later."""
    if channel == "email":
        send_mail(
            subject="Your PhotoBooth signin code",
            message=f"Your code is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[value],
        )
    else:
        print(f"[SMS to {value}] Your code is {code}")


def verify_otp(channel, value, code):
    """Check a submitted code. Returns True only if everything passes."""
    otp = (
        OTP.objects.filter(channel=channel, value=value, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if otp is None or otp.expires_at < timezone.now():
        return False

    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        return False

    if not check_password(code, otp.code_hash):
        otp.attempts += 1          # count the wrong guess
        otp.save()
        return False

    otp.is_used = True             # one code, one signin
    otp.save()
    return True