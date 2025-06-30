from django import forms
from .models import EmployeeProfile, Skill

class EmployeeProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.MultipleHiddenInput(),
        required=False, # スキルがなくても良い
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            'enterprise_id', 'name', 'department', 'dte',
            'ml', 'mail_address', 'statement_id',
            'is_manager', 'is_hr',
            'phone_number', 'date_of_birth', 'bio', 'skills',
        ]
        labels = {
            'ml': 'ML',
        }
        widgets = {
             'ml': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
