from django.contrib.auth.models import AbstractUser
from django.db import models

# AbstractUser already gives us: username, email, password, is_active, etc.
# We only add the extra columns from our whiteboard table.
class User(AbstractUser):
    name = models.CharField(max_length=100)
    mob = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.username