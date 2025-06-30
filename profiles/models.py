from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    enterprise_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    dte = models.CharField(max_length=100)
    ml = models.DateField()
    mail_address = models.CharField(max_length=100)
    birth_day = models.DateField()
    statement_id = models.CharField(max_length=10)
    is_manager = models.BooleanField()
    is_hr = models.BooleanField()

    # 既存項目
    bio = models.TextField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return f"{self.enterprise_id} - {self.name}"