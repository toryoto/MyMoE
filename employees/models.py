from django.contrib.auth.models import AbstractUser
from django.db import models
from departments.models import Department, DTE
from django.core.exceptions import ValidationError

class Employee(AbstractUser):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    dte = models.ForeignKey(DTE, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    is_hr = models.BooleanField(default=False)
    force_password_change = models.BooleanField(default=False)

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