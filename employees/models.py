from django.contrib.auth.models import AbstractUser
from django.db import models

class Employee(AbstractUser):
    # Add any additional fields for your employee model here
    # For example:
    # department = models.CharField(max_length=100, blank=True)
    pass