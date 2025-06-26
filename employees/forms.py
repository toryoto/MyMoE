from django.contrib.auth.forms import UserCreationForm
from .models import Employee

class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = ('username', 'email')
