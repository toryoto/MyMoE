from django.contrib.auth.forms import UserCreationForm
from .models import Employee
from django.core.validators import RegexValidator

class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = ('username', 'email')

from django import forms

class SignUpForm(forms.Form):
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