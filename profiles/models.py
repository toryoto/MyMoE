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
    ML_CHOICES = [
        ('1','SMD'),
        ('2-4','Managing Director'),
        ('5','Associate Director'),
        ('6','Senior Manager'),
        ('7','Manager'),
        ('8','Associate Manager'),
        ('9','Team Lead/Consultant'),
        ('10','Sonior Analyst'),
        ('11','Analyst'),
        ('12','Associate'),
        ('13','New Associate')
    ]
    ml = models.CharField(max_length=50,choices= ML_CHOICES ,default='11')
    mail_address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    statement_id = models.CharField(max_length=10)
    is_manager = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)

    # ✅ 追加：電話番号
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # 既存項目
    bio = models.TextField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return f"{self.enterprise_id} - {self.name}"
