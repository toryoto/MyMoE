from django.contrib.auth.forms import UserCreationForm
from .models import Employee
from django.core.validators import RegexValidator
from django import forms

class EmployeeCreationForm(UserCreationForm):
    username = forms.CharField(
        label='ユーザーID',
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+\.[a-zA-Z]+$',
                message='EIDのみ入力可能です。'
            )
        ]
    )
    
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = ('username', 'email')


