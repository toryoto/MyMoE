from django import forms
from .models import EmployeeProfile, Skill, PreEmploymentHistory
from django.forms import ClearableFileInput, inlineformset_factory

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

class PreEmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = PreEmploymentHistory
        fields = ['company_name', 'job_title', 'job_role', 'job_description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


PreEmploymentHistoryFormSet = inlineformset_factory(
    EmployeeProfile,
    PreEmploymentHistory,
    form=PreEmploymentHistoryForm,
    extra=1,
    can_delete=True
)
