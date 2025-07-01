from django.contrib.auth.models import AbstractUser
from django.db import models
from departments.models import Department, DTE
from django.core.exceptions import ValidationError


class Employee(AbstractUser):
    ML_CHOICES = [
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    dte = models.ForeignKey(DTE, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    is_hr = models.BooleanField(default=False)
    force_password_change = models.BooleanField(default=False)
    ml = models.CharField(max_length=50, choices=ML_CHOICES, null=True, blank=True, default='11')

    def clean(self):
        super().clean()
        if self.department and self.dte:
            if self.dte.department != self.department:
                raise ValidationError({'dte': 'The selected DTE does not belong to the selected Department.'})

    def save(self, *args, **kwargs):
        if self.department and self.department.code == 'HR':
            self.is_hr = True
        else:
            self.is_hr = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username