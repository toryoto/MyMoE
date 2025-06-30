from django import forms
from django.contrib.auth import get_user_model
from .models import EmployeeProfile, Skill, PreEmploymentHistory
from django.forms import ClearableFileInput, inlineformset_factory
from django.conf import settings

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
        exclude = ('employee_profile',)
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '会社名を入力してください'}),
            'job_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '役職を入力してください'}),
            'job_role': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '職種を入力してください'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'job_description': forms.Textarea(attrs={'class': 'form-input form-textarea', 'placeholder': '職務内容を詳しく記入してください'}),
        }

PreEmploymentHistoryFormSet = inlineformset_factory(
    EmployeeProfile,
    PreEmploymentHistory,
    form=PreEmploymentHistoryForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)