from django import forms
from .models import EmployeeProfile
from django.core.validators import RegexValidator

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['phone_number', 'date_of_birth', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

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
