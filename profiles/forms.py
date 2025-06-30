from django import forms
from .models import EmployeeProfile, Skill
from django.forms import ClearableFileInput

class EmployeeProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.MultipleHiddenInput(),
        required=False, # スキルがなくても良い
    )

    class Meta:
        model = EmployeeProfile

        fields = ['phone_number', 'date_of_birth', 'bio', 'photo', 'skills']


        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'photo': ClearableFileInput(),
        }
