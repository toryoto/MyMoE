from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True) 
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

class PreEmploymentHistory(models.Model):
    """入社前の職歴"""
    employee_profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='pre_employment_histories')
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_role = models.CharField(max_length=100)
    job_description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.employee_profile.user.username} - {self.company_name}"
