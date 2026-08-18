from django.contrib.auth.models import AbstractUser
from django.db import models

# AbstractUser already gives us: username, email, password, is_active, etc.
# We only add the extra columns from our whiteboard table.
class User(AbstractUser):
    name = models.CharField(max_length=100)
    mob = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.username


class OTP(models.Model):
    channel = models.CharField(max_length=10)      # "mobile" or "email"
    value = models.CharField(max_length=100)       # the number / address it went to
    code_hash = models.CharField(max_length=128)   # hashed, never the raw code
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
