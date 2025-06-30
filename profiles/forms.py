from django import forms
from .models import EmployeeProfile, Skill
from django.forms import ClearableFileInput
import re

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

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # ハイフンを含んでいるかどうかをチェック
        pattern = r'^\d{2,4}-\d{2,4}-\d{3,4}$'
        if not re.match(pattern, phone_number):
            raise forms.ValidationError("電話番号は「090-1234-5678」の形式で入力してください")

        return phone_number