from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    full_name = models.CharField(null=True, max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_admin =  models.BooleanField(default=False)
    address = models.CharField(null=True, max_length=255)
    date_created =  models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.username
