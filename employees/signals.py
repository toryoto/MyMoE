from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from profiles.models import EmployeeProfile

@receiver(post_save, sender=Employee)
def create_or_update_employee_profile(sender, instance, created, **kwargs):
    if created:
        EmployeeProfile.objects.create(user=instance)
    instance.employeeprofile.save()
